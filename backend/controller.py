from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pathlib import Path
import tempfile
import subprocess

class LuaLatexManager:
    def __init__(self):
        self.tmp_path = Path(tempfile.gettempdir())
        print(self.tmp_path)

    def compile(self, code: str):
        # Create file
        tex_path = self.tmp_path / "code.tex"

        with open(tex_path, "w") as tf:
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



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CodeDTO(BaseModel):
    code: str

lua = LuaLatexManager()

@app.post("/compile-lualatex")
def compile_lualatex(request: Request, codeDTO: CodeDTO):
    filename = lua.compile(codeDTO.code)

    headers = {'Access-Control-Expose-Headers': 'Content-Disposition'}
    return FileResponse(filename, filename="result.pdf", headers=headers)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=6969)
