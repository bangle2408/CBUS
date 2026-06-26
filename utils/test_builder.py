from __future__ import annotations

import random
from pathlib import Path
import hydra
from hydra.utils import to_absolute_path
from omegaconf import DictConfig, OmegaConf

def create_edge_matrix(size: int, min_cost: int, max_cost: int) -> list[list[int]]:
    matrix = [[0 for _ in range(size)] for _ in range(size)]

    for i in range(size):
        for j in range(i + 1, size):
            matrix[i][j] = matrix[j][i] = random.randint(min_cost, max_cost)

    return matrix

def build_test(folder: Path, cfg: DictConfig, seed: int) -> Path:
    n = int(cfg.n)
    k = int(cfg.k)
    min_edge = int(cfg.min_edge)
    max_edge = int(cfg.max_edge)

    if n != int(folder.name):
        raise ValueError(f"Mismatch size!")

    random.seed(seed + n)
    size = 2 * n + 1
    matrix = create_edge_matrix(size, min_edge, max_edge)
    output_path = folder / "task.inp"

    with output_path.open("w", encoding="utf-8") as file:
        file.write(f"{n} {k}\n")
        for row in matrix:
            file.write(" ".join(map(str, row)))
            file.write("\n")

    return output_path

@hydra.main(version_base=None, config_path="../cfg", config_name="config")
def main(cfg: DictConfig) -> None:
    seed = cfg.seed
    data_dir = Path(to_absolute_path(cfg.path.DATA))
    config_dir = Path(to_absolute_path(cfg.path.TEST))

    test = [3,4,5,6,7,8,9,10,11,12,13,14,15,16,20,50,100,200,300,400,500,600,700,800,900,1000]

    print(f"[seed] create test with seed {seed}")
    for t in test:
        data_f = data_dir / str(t)
        conf = OmegaConf.load(config_dir / f"{t}.yaml")
        output_path = build_test(data_f, conf, seed)

        print(f"[create] create {t}.inp")

if __name__ == "__main__":
    main()
