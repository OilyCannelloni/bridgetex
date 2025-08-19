from pathlib import Path
import subprocess


class LuaDriver:
    def __init__(self):
        self.tmp_path = Path(__file__).parent.resolve() / "temp"
        print(self.tmp_path)

    def compile(self, code: str):
        # Create file
        tex_path = self.tmp_path / "code.tex"

        with open(tex_path, "w", encoding="utf-8") as tf:
            tf.write("\\documentclass{article}\n\\usepackage{import}\n\\import{./lib/}{bridge.sty}\n")
            tf.write(code)
        
        # Compile
        print("Compilating")
        try:    
            out = subprocess.check_output(
                f"lualatex -interaction=nonstopmode --output-directory={self.tmp_path} --jobname=result code.tex",
                stderr=subprocess.STDOUT,
                shell=True,
                timeout=10)
            print(out.decode())

        except subprocess.CalledProcessError as e:
            print("Error")
            print(e.output.decode())
        except subprocess.TimeoutExpired:
            print("Timeout")

        return self.tmp_path / Path("result.pdf")

