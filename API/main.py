# Copyright (C) 2021 Humanitarian OpenStreetmap Team

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Humanitarian OpenStreetmap Team
# 1100 13th Street NW Suite 800 Washington, D.C. 20005
# <info@hotosm.org>
import time


import sentry_sdk

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_versioning import VersionedFastAPI

from src.galaxy.config import config

# from .changesets.routers import router as changesets_router
# from .data.routers import router as data_router
from .auth.routers import router as auth_router
from .countries.routers import router as countries_router
from .data_quality import router as data_quality_router

# from .trainings import router as training_router
from .hashtag_stats import router as hashtag_router
from .mapathon import router as mapathon_router
from .osm_users import router as osm_users_router

# from .test_router import router as test_router
from .status import router as status_router
from .tasking_manager import router as tm_router

# only use sentry if it is specified in config blocks
if config.get("SENTRY", "dsn", fallback=None):
    sentry_sdk.init(
        dsn=config.get("SENTRY", "dsn"),
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=config.get("SENTRY", "rate"),
    )

run_env = config.get("API_CONFIG", "env", fallback="prod")
if run_env.lower() == "dev":
    # This is used for local setup for auth login
    import os

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app = FastAPI(title="Galaxy API")

# app.include_router(test_router)
app.include_router(countries_router)
# app.include_router(changesets_router)
app.include_router(auth_router)
app.include_router(mapathon_router)
# app.include_router(data_router)
app.include_router(osm_users_router)
app.include_router(data_quality_router)
# app.include_router(training_router)
app.include_router(hashtag_router)
app.include_router(tm_router)
app.include_router(status_router)

app = VersionedFastAPI(
    app, enable_latest=True, version_format="{major}", prefix_format="/v{major}"
)


origins = ["*"]


@app.middleware("http")
async def add_process_time_header(request, call_next):
    """Times request and knows response time and pass it to header in every request

    Args:
        request (_type_): _description_
        call_next (_type_): _description_

    Returns:
        header with process time
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(f"{process_time:0.4f} sec")
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

