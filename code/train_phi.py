'''
LinCIR
Copyright (c) 2023-present NAVER Corp.
CC BY-NC-4.0 (https://creativecommons.org/licenses/by-nc/4.0/)
'''
import json
import os
import pickle
import random
import math
from argparse import ArgumentParser
from pathlib import Path
from typing import Literal, Tuple, Dict, List, Set
import logging
import time

import numpy as np
import torch
import torch.nn.functional as F
from tqdm import tqdm

from loader import build_loader, CIRRDataset
from encode_with_pseudo_tokens import encode_with_pseudo_tokens_HF
from models import build_text_encoder, Phi, EMAModel
from utils import extract_image_features, extract_pseudo_tokens_with_phi
from validate import cirr_compute_val_metrics

import transformers
from transformers import get_scheduler
from accelerate import Accelerator, DeepSpeedPlugin
from accelerate.logging import get_logger
from accelerate.utils import set_seed
from accelerate.state import AcceleratorState
from accelerate.logging import get_logger


logger = get_logger(__name__)


def parse_args():
    parser = ArgumentParser()

    parser.add_argument("--output_dir", default="trained_models", type=str,
                        help="The output directory where the model predictions and checkpoints will be written")
    parser.add_argument("--logging_dir", default="logs", type=str, help="tensorboard logs will saved here")
    parser.add_argument("--cache_dir", default="./hf_models", type=str,
                        help="Path to model cache folder")
    parser.add_argument("--report_to", default="tensorboard", type=str, help="")
    parser.add_argument("--local_rank", type=int, default=-1, help="For distributed training: local_rank")

    parser.add_argument("--clip_model_name", default="giga", type=str,
                        help="CLIP model to use, e.g 'large', 'giga'")
    parser.add_argument("--cirr_dataset_path", type=str, default=None,
                        help="Path to CIRR dataset. [NHOM8] Optional: without it, validation and phi_best are skipped (smoke tests)")
    parser.add_argument("--keywords_path", type=str, help="Path to keywords json file")
    parser.add_argument("--resume", default=None, type=str, help="Path to pretrained ckpt")

    parser.add_argument("--use_8bit_adam", action="store_true", help="Whether or not to use 8-bit Adam from bitsandbytes.")
    parser.add_argument("--lr_scheduler", type=str, default="constant",
                        choices=["linear", "cosine", "cosine_with_restarts", "polynomial", "constant", "constant_with_warmup"],
                        help="")
    parser.add_argument("--lr_warmup_steps", type=int, default=500, help="Number of steps for the warmup in the lr scheduler.")
    parser.add_argument("--max_train_steps", type=int, default=50000, help="Total number of training steps to perform")
    parser.add_argument("--phi_dropout", default=0.5, type=float, help="Dropout probability for the phi network")
    parser.add_argument("--l2_normalize", action="store_true", help="Whether or not to use l2 normalization")
    parser.add_argument("--batch_size", default=256, type=int, help="Phi training batch size")
    parser.add_argument("--num_workers", default=10, type=int, help="Number of workers")
    parser.add_argument("--learning_rate", default=1e-4, type=float, help="Learning rate")
    parser.add_argument("--weight_decay", type=float, default=0.01, help="Weight decay")
    parser.add_argument("--gradient_accumulation_steps", default=1, type=int, help="Number of updates steps to accumulate before performing a backward/update pass")
    parser.add_argument("--max_grad_norm", default=None, type=float, help="Max gradient norm.")
    parser.add_argument("--mixed_precision", default=None, type=str, choices=["no", "fp16", "bf16"], help="mixed precision")
    parser.add_argument("--validation_steps", default=None, type=int, help="Validation frequency expressed in epochs")
    parser.add_argument("--checkpointing_steps", default=None, type=int, help="Save a checkpoint of the training state every X updates")
    parser.add_argument("--use_ema", action="store_true", help="Whether to use EMA model.")

    parser.add_argument("--seed", type=int, default=None, help="seed for reproducibility")

    # [NHOM8] training data control (smoke tests / scaled-down runs). Defaults reproduce the original setup.
    parser.add_argument("--caption_datasets", nargs="+", default=["dataset1", "dataset2", "dataset3"],
                        help="Subset of HF caption corpora: dataset1=CC3M, dataset2=SD prompts, dataset3=Midjourney prompts")
    parser.add_argument("--train_captions_file", type=str, default=None, help="Plain-text captions, one per line (replaces HF corpora)")
    parser.add_argument("--max_captions", type=int, default=None, help="Random subset of captions (fixed data seed 0)")
    # [NHOM8] Improvement A: contrastive (InfoNCE) term added to the SMP MSE loss
    parser.add_argument("--infonce_weight", type=float, default=0.0, help="lambda; 0 disables (original LinCIR)")
    parser.add_argument("--infonce_temp", type=float, default=0.07, help="InfoNCE temperature tau")
    # [NHOM8] Improvement B: direction-aware noise, n = alpha * delta + Unif(0,1) * N(0,1)
    parser.add_argument("--gap_noise_alpha", type=float, default=0.0, help="alpha; 0 disables (original LinCIR)")
    parser.add_argument("--gap_vector_path", type=str, default=None, help="Tensor file with delta = mean(image) - mean(text) embeddings")
    # [NHOM8] Improvement C: mask only the most informative keywords by IDF
    parser.add_argument("--idf_path", type=str, default=None, help="JSON {word: idf} from scripts/compute_idf.py")
    parser.add_argument("--idf_keep_ratio", type=float, default=1.0, help="Fraction of keywords (highest IDF first) replaced by [$]; 1.0 = original")

    args = parser.parse_args()

    env_local_rank = int(os.environ.get("LOCAL_RANK", -1))
    if env_local_rank != -1 and env_local_rank != args.local_rank:
        args.local_rank = env_local_rank

    return args


def save_phi(name: str, cur_epoch: int, model_to_save: Phi, training_path: Path) -> None:
    """
    Save the weights of Phi during training
    """
    models_path = os.path.join(training_path, "checkpoints")
    os.makedirs(models_path, exist_ok=True)
    model_name = model_to_save.__class__.__name__
    torch.save({
        'epoch': cur_epoch,
        model_name: model_to_save.state_dict(),
    }, os.path.join(models_path, f'{name}.pt'))


def train_phi(args):
    # We are going to use the pre-extracted clip image features. so we do not need image_encoder anymore.

    ### init accelerator here
    logging_dir = os.path.join(args.output_dir, args.logging_dir)
    accelerator = Accelerator(
            gradient_accumulation_steps=args.gradient_accumulation_steps,
            mixed_precision=args.mixed_precision,
            log_with=args.report_to,
            project_dir=logging_dir,
    )

    os.makedirs(args.output_dir, exist_ok=True)

    logging.basicConfig(
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%m/%d/%Y %H:%M:%S",
            level=logging.INFO,
    )
    logger.info(accelerator.state, main_process_only=False)

    if accelerator.is_local_main_process:
        transformers.utils.logging.set_verbosity_info()
    else:
        transformers.utils.logging.set_verbosity_error()

    if args.seed is not None:
        set_seed(args.seed)

    ### Define the text encoder from clip
    image_encoder, clip_preprocess, text_encoder, tokenizer = build_text_encoder(args)

    ### Define the phi model
    phi = Phi(input_dim=text_encoder.config.projection_dim,
                    hidden_dim=text_encoder.config.projection_dim * 4,
                    output_dim=text_encoder.config.hidden_size, dropout=args.phi_dropout)

    if args.resume:
        phi.load_state_dict(
                torch.load(args.resume, map_location=accelerator.device)[
                phi.__class__.__name__])


    ### GPU handling
    weight_dtype = torch.float32
    if accelerator.mixed_precision == "fp16":
        weight_dtype = torch.float16
    elif accelerator.mixed_precision == "bf16":
        weight_dtype = torch.bfloat16

    image_encoder.to(accelerator.device, dtype=weight_dtype)
    text_encoder.to(accelerator.device, dtype=weight_dtype)

    image_encoder.requires_grad_(False)
    text_encoder.requires_grad_(False)

    if args.use_ema:
        import copy
        ema_phi = copy.deepcopy(phi)
        ema_phi = EMAModel(ema_phi.parameters())
        ema_phi.to(accelerator.device, dtype=weight_dtype)

    # [NHOM8] Improvement B: load the modality-gap direction once
    gap_vector = None
    if args.gap_noise_alpha > 0:
        assert args.gap_vector_path, "--gap_vector_path is required when --gap_noise_alpha > 0"
        gap_vector = torch.load(args.gap_vector_path, map_location="cpu").float().to(accelerator.device)
        assert gap_vector.shape[-1] == text_encoder.config.projection_dim, "gap vector dim does not match the backbone"

    ### Define the train datasets
    print('pytorch loader')
    train_dataset = build_loader(args, tokenizer, accelerator)
    if len(train_dataset) == 0:  # [NHOM8] the original `while True` loop would spin forever on an empty loader
        raise ValueError(f"Fewer training captions than one batch ({args.batch_size}); lower --batch_size or add captions")

    ## evaluator
    if accelerator.is_main_process and args.cirr_dataset_path:  # [NHOM8] validation is optional
        ## Define CIRR validation set
        cirr_relative_val_dataset = CIRRDataset(args.cirr_dataset_path, 'val', 'relative', clip_preprocess)
        cirr_classic_val_dataset = CIRRDataset(args.cirr_dataset_path, 'val', 'classic', clip_preprocess)

        # Extract the features for the CIRR validation set
        cirr_val_index_features, cirr_val_index_names = extract_image_features(cirr_classic_val_dataset, image_encoder)

    # Define the optimizer, the loss and the grad scaler
    if args.use_8bit_adam:
        try:
            import bitsandbytes as bnb
        except ImportError:
            raise ImportError(
                    "Please install bitsandbytes to use 8-bit Adam. You can do so by running `pip install bitsandbytes`"
            )
        optimizer_cls = bnb.optim.AdamW8bit
    else:
        optimizer_cls = torch.optim.AdamW

    optimizer = optimizer_cls(phi.parameters(),
                              lr=args.learning_rate,
                              weight_decay=args.weight_decay)

    lr_scheduler = get_scheduler(
            args.lr_scheduler,
            optimizer=optimizer,
            num_warmup_steps=args.lr_warmup_steps * args.gradient_accumulation_steps * accelerator.num_processes,
            num_training_steps=args.max_train_steps * args.gradient_accumulation_steps * accelerator.num_processes,
    )

    phi, optimizer, lr_scheduler, train_dataset = accelerator.prepare(
            phi, optimizer, lr_scheduler, train_dataset
    )

    if accelerator.is_main_process:
        # [NHOM8] TensorBoard hparams accept only int/float/str/bool: stringify lists and None (crashed on Kaggle)
        tracker_config = {k: v if isinstance(v, (int, float, str, bool)) else str(v) for k, v in vars(args).items()}
        accelerator.init_trackers("zeroshot-cir", config=tracker_config)

    # Start with the training loop
    total_batch_size = args.batch_size * accelerator.num_processes * args.gradient_accumulation_steps

    logger.info("***** Running training *****")
    logger.info(f"  Instantaneous batch size per device = {args.batch_size}")
    logger.info(f"  Total train batch size (w. parallel, distributed & accumulation) = {total_batch_size}")
    logger.info(f"  Gradient Accumulation steps = {args.gradient_accumulation_steps}")
    logger.info(f"  Total steps = {args.max_train_steps}")

    phi.train()

    train_loss = 0.0
    global_step = 0
    best_recall = -1
    history = []  # [NHOM8] per-validation metrics, written to train_metrics.json
    start_time = time.time()

    progress_bar = tqdm(range(global_step, args.max_train_steps), disable=not accelerator.is_local_main_process)
    progress_bar.set_description("Steps")

    while True:
        for idx, (original_tokens, replaced_tokens, indicators) in enumerate(train_dataset):
            original_tokens = original_tokens.to(accelerator.device)
            replaced_tokens = replaced_tokens.to(accelerator.device)

            org = text_encoder(input_ids=original_tokens)
            original_text_embeddings, original_last_hidden_states = org.text_embeds, org.last_hidden_state
            input_features = original_text_embeddings.clone()
            input_features += 1.0 * torch.rand(input_features.shape[0], device=input_features.device).unsqueeze(-1) * torch.randn(input_features.shape, device=input_features.device)
            if gap_vector is not None:  # [NHOM8] Improvement B: shift towards the image side of the modality gap
                input_features += args.gap_noise_alpha * gap_vector.to(input_features.dtype)

            # normalize test
            if args.l2_normalize:
                input_features = F.normalize(input_features, dim=-1)
            #################

            estimated_token_embeddings = phi(input_features)

            replaced_text_embeddings, replaced_last_hidden_states = encode_with_pseudo_tokens_HF(text_encoder, replaced_tokens, estimated_token_embeddings, return_last_states=True)

            loss = F.mse_loss(replaced_text_embeddings.float(), original_text_embeddings.float(), reduction="mean")
            if args.infonce_weight > 0:  # [NHOM8] Improvement A: in-batch contrastive term (symmetric InfoNCE)
                z_hat = F.normalize(replaced_text_embeddings.float(), dim=-1)
                z = F.normalize(original_text_embeddings.float(), dim=-1)
                logits = z_hat @ z.t() / args.infonce_temp
                targets = torch.arange(logits.shape[0], device=logits.device)
                infonce = 0.5 * (F.cross_entropy(logits, targets) + F.cross_entropy(logits.t(), targets))
                loss = loss + args.infonce_weight * infonce

            avg_loss = accelerator.gather(loss.repeat(args.batch_size)).mean()
            train_loss += avg_loss.item() / args.gradient_accumulation_steps

            # Backpropagation
            accelerator.backward(loss)
            if accelerator.sync_gradients and args.max_grad_norm is not None:
                accelerator.clip_grad_norm_(phi.parameters(), args.max_grad_norm)  # [NHOM8] fix typo arg -> args
            optimizer.step()
            lr_scheduler.step()
            optimizer.zero_grad()
            
            if accelerator.sync_gradients:
                if args.use_ema:
                    ema_phi.step(phi.module.parameters())
                progress_bar.update(1)
                global_step += 1
                accelerator.log({"train/train_loss": train_loss}, step=global_step)
                train_loss = 0.0

                accelerator.log({'train/lr': lr_scheduler.get_last_lr()[0]}, step=global_step)
                accelerator.log({'train/preproc_rate': torch.sum(indicators).item() / len(indicators)}, step=global_step)
                if args.checkpointing_steps and global_step % args.checkpointing_steps == 0:
                    if accelerator.is_main_process:
                        logger.info(f"model saving... step: {global_step}")
                        save_phi(f"phi_{global_step:09}", global_step, accelerator.unwrap_model(phi), args.output_dir)
                        save_phi(f"phi_latest", global_step, accelerator.unwrap_model(phi), args.output_dir)
                    if args.use_ema:
                        phi_for_saving = copy.deepcopy(accelerator.unwrap_model(phi))
                        ema_phi.copy_to(phi_for_saving.parameters())
                        save_phi(f"ema_phi_{global_step:09}", global_step, phi_for_saving, args.output_dir)
                        save_phi(f"ema_phi_latest", global_step, phi_for_saving, args.output_dir)

                if args.validation_steps and args.cirr_dataset_path and (global_step % args.validation_steps == 0 or global_step == 50):
                    if accelerator.is_main_process:
                        logger.info(f"evaluate model... step: {global_step}")

                        if args.use_ema:
                            phi_for_eval = copy.deepcopy(accelerator.unwrap_model(phi))
                            ema_phi.copy_to(phi_for_eval.parameters())
                        else:
                            phi_for_eval = phi

                        phi_for_eval.eval()

                        # Extract the pseudo tokens for the CIRR validation set using Phi
                        cirr_val_pseudo_tokens, cirr_val_ref_names_list = extract_pseudo_tokens_with_phi(image_encoder, phi_for_eval,
                                                                                                         cirr_relative_val_dataset, args)
                        cirr_val_pseudo_tokens = cirr_val_pseudo_tokens.to(accelerator.device)

                        # Compute the CIRR validation metrics
                        cirr_results_dict = cirr_compute_val_metrics(cirr_relative_val_dataset, text_encoder,
                                                                     cirr_val_index_features, cirr_val_index_names,
                                                                     cirr_val_ref_names_list, cirr_val_pseudo_tokens)
                        check_list = ['cirr_recall_at1', 'cirr_recall_at5', 'cirr_recall_at10', 'cirr_recall_at50']
                        for check_key in check_list:
                            accelerator.log({f"validate/{check_key}": cirr_results_dict[check_key]}, step=global_step)
                        print(json.dumps(cirr_results_dict, indent=4))
                        history.append({"step": global_step, "elapsed_sec": round(time.time() - start_time, 1), **cirr_results_dict})

                        # Save the best model.
                        if args.checkpointing_steps:
                            if cirr_results_dict['cirr_recall_at1'] > best_recall:
                                best_recall = cirr_results_dict['cirr_recall_at1']
                                logger.info(f"best model saving... step: {global_step}")
                                save_phi("phi_best", global_step, accelerator.unwrap_model(phi), args.output_dir)

                        phi.train()

            if global_step >= args.max_train_steps:
                if accelerator.is_main_process:  # [NHOM8] record timing and validation history, always keep the last weights
                    save_phi("phi_latest", global_step, accelerator.unwrap_model(phi), args.output_dir)
                    best = max(history, key=lambda h: h["cirr_recall_at1"]) if history else None
                    peak_mem = torch.cuda.max_memory_allocated() / 2**30 if torch.cuda.is_available() else None
                    with open(os.path.join(args.output_dir, "train_metrics.json"), "w") as f:
                        json.dump({"train_hours": round((time.time() - start_time) / 3600, 4),
                                   "sec_per_step": round((time.time() - start_time) / max(global_step, 1), 3),
                                   "peak_gpu_mem_gb": peak_mem and round(peak_mem, 2),
                                   "num_processes": accelerator.num_processes,
                                   "device": str(accelerator.device), "steps": global_step,
                                   "best": best, "history": history, "args": vars(args)}, f, indent=2)
                exit()


if __name__ == '__main__':
    args = parse_args()

    train_phi(args)
