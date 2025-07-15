from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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


@app.post("/compile-lualatex")
def compile_lualatex(request: Request, codeDTO: CodeDTO):
    print(request)
    print(codeDTO.code)
    return "Yay"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=6969)
