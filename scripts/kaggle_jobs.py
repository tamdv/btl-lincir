"""[NHOM8] Helpers used by notebooks/kaggle_lincir.ipynb (kept here so they can be tested on the Mac).

- find_input(pattern): first match under /kaggle/input (or --input_root), for files left by earlier notebook versions
- run_parallel(jobs, gpus, time_limit_h, est_hours): run jobs (lists of argv) on separate GPUs, one at a time per GPU,
  skipping jobs that would not finish before the session time limit
- prefetch(clip_model_name): download CLIP, tokenizer and caption corpora once, before parallel jobs start
"""
import glob
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

INPUT_ROOT = os.environ.get("KAGGLE_INPUT_ROOT", "/kaggle/input")
START = time.time()


def find_input(pattern, root=None):
    hits = sorted(glob.glob(os.path.join(root or INPUT_ROOT, "**", pattern), recursive=True))
    return hits[0] if hits else None


def elapsed_h():
    return (time.time() - START) / 3600


def run_parallel(jobs, gpus=(0, 1), time_limit_h=11.0, est_hours=3.5, log_dir="experiments/job_logs"):
    """jobs: list of (name, argv). Each GPU takes the next job when free. Returns {name: returncode or 'skipped'}."""
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    queue, results, lock, durations = list(jobs), {}, threading.Lock(), []

    def worker(gpu):
        while True:
            with lock:
                if not queue:
                    return
                est = max([est_hours] + durations)  # learn from finished jobs (parallel runs can be slower)
                if elapsed_h() + est > time_limit_h:
                    for name, _ in queue:
                        results[name] = "skipped"
                    print(f"[gpu{gpu}] stop: {elapsed_h():.1f} h used + {est:.1f} h > limit {time_limit_h} h", flush=True)
                    queue.clear()
                    return
                name, argv = queue.pop(0)
            env = {**os.environ, "CUDA_VISIBLE_DEVICES": str(gpu)}
            t = time.time()
            print(f"[gpu{gpu}] start {name} at {elapsed_h():.2f} h", flush=True)
            with open(f"{log_dir}/{name}.log", "w") as log:
                rc = subprocess.run(argv, env=env, stdout=log, stderr=subprocess.STDOUT).returncode
            with lock:
                results[name] = rc
                if rc == 0:
                    durations.append((time.time() - t) / 3600)
            print(f"[gpu{gpu}] {'done' if rc == 0 else 'FAILED'} {name} ({(time.time() - t) / 3600:.2f} h)", flush=True)

    threads = [threading.Thread(target=worker, args=(g,)) for g in gpus]
    for th in threads:
        th.start()
        time.sleep(30)  # stagger start-up (model loading, caption tokenizer workers)
    for th in threads:
        th.join()
    return results


def prefetch(clip_model_name="large", corpora=("dataset1", "dataset2", "dataset3"), code_dir="code"):
    code = f"""
import sys; sys.path.insert(0, '.')
from types import SimpleNamespace
from models import build_text_encoder
build_text_encoder(SimpleNamespace(clip_model_name='{clip_model_name}', mixed_precision='fp16', cache_dir='./hf_models'))
import datasets
names = {{'dataset1': 'dangne/gcc_caption_only', 'dataset2': 'FredZhang7/stable-diffusion-prompts-2.47M',
          'dataset3': 'Geonmo/midjourney-prompts-only'}}
for k in {list(corpora)!r}:
    print(k, len(datasets.load_dataset(names[k], cache_dir='./datasets/' + k)['train']))
"""
    subprocess.run([sys.executable, "-c", code], cwd=code_dir, check=True)
