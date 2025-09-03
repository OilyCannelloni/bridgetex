from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
from pydantic import BaseModel

from .tc.tc_downloader import TCResultsDriver
from .lua.lua_compiler import LuaDriver
from .system.tempfile_service import TempFileService
from .tc.models import CodeDTO, DownloadTcDTO


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
def compile_lualatex(codeDTO: CodeDTO):
    filename = lua_driver.compile(codeDTO.code)

    headers = {'Access-Control-Expose-Headers': 'Content-Disposition'}
    return FileResponse(filename, filename="result.pdf", headers=headers)


@app.post("/download-tc-init")
async def download_tc(download_tc_DTO: DownloadTcDTO):
    id = tc_driver.create_session(download_tc_DTO)
    return {"session_id": id}
   

@app.get("/download-tc-sse/{session_id}")
def download_tc_sse(session_id: str):
    headers = {
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no"
    }
    return StreamingResponse(tc_driver.download_boards(session_id), media_type="text/event-stream", headers=headers)


@app.get("/download-file/{session_id}/{file_type}")
async def download_tc_file(session_id: str, file_type: str):
    path = tc_driver.output_dir / f"{session_id}.{file_type}"
    headers = {'Access-Control-Expose-Headers': 'Content-Disposition'}
    return FileResponse(path, filename=f"{'analysis' if file_type == "tex" else 'board_set'}.{file_type}", headers=headers)


@app.on_event("startup")
@repeat_every(seconds=60 * 5)
def remove_temp_files():
    TempFileService.clear_temp_files()
    tc_driver.clear_sessions()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=6969)
