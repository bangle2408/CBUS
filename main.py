import hydra
from omegaconf import DictConfig, OmegaConf
from hydra.utils import to_absolute_path
from pathlib import Path

from utils.logger import Logger
from utils.evaluator import Evaluator

@hydra.main(version_base=None, config_path="cfg", config_name="config")
def main(cfg: DictConfig):
    L = Logger(cfg.path.RES)
    E = Evaluator()
    test = list(range(3,17)) + [20,50,100,200,300,400,500,600,700,800,900,1000]

    for t in test:
        path = Path(to_absolute_path(cfg.path.DATA)) / f"{t}" / "task.inp"
        config_dir = Path(to_absolute_path(cfg.path.TEST)) / f"{t}.yaml"
        conf = OmegaConf.load(config_dir)
        
        n,k,c,timelimit = E.read_input(path, conf)
        
        size, scores, runtime = E.evaluate(n,k,c,timelimit)

        L.log(size, k, scores, runtime)

    print("[info] Done.")


if __name__ == "__main__":
    main()