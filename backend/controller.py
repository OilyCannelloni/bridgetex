from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
from pydantic import BaseModel

from .tc.tc_downloader import TCResultsDriver
from .lua.lua_compiler import LuaDriver
from .system.tempfile_service import TempFileService




class CodeDTO(BaseModel):
    code: str

class DownloadTcDTO(BaseModel):
    url: str
    boards: list | None


lua_driver = LuaDriver()
tc_driver = TCResultsDriver()

"""
Scheduler for repeated tasks
"""


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


"""
Endpoints
"""

@app.post("/compile-lualatex")
def compile_lualatex(request: Request, codeDTO: CodeDTO):
    filename = lua_driver.compile(codeDTO.code)

    headers = {'Access-Control-Expose-Headers': 'Content-Disposition'}
    return FileResponse(filename, filename="result.pdf", headers=headers)


@app.post("/download-tc-init")
async def download_tc(request: Request, download_tc_DTO: DownloadTcDTO):
    return StreamingResponse(tc_driver.download_boards(download_tc_DTO.url, download_tc_DTO.boards), media_type="text/event_stream")

@app.get("/download-tc-file/{hex_id}")
def download_tc_file(request: Request, hex_id: str):
    path = tc_driver.output_dir / f"analysis_{hex_id}.tex"
    headers = {'Access-Control-Expose-Headers': 'Content-Disposition'}
    return FileResponse(path, filename="analysis.tex", headers=headers)


@app.on_event("startup")
@repeat_every(seconds=60 * 5)
def remove_temp_files():
    TempFileService.clear_temp_files()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=6969)
