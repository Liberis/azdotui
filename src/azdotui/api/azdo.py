# api/azdo.py

import asyncio
from datetime import datetime, timedelta

import aiohttp
from azdotui.config.logger import logger
from azdotui.config.settings import AZDO_ORGANIZATION, AZDO_PAT


class AzureDevOpsClient:
    def __init__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100)
        )
        self.auth = aiohttp.BasicAuth('', AZDO_PAT)
        self.base_url = f'https://dev.azure.com/{AZDO_ORGANIZATION}'
        self.projects_cache = None
        self.projects_cache_expiry = datetime.utcnow()
        self.pipelines_cache = {}
        self.pipelines_cache_expiry = {}

    async def close(self):
        try:
            await self.session.close()
            logger.info("AzureDevOpsClient session closed successfully.")
        except Exception as e:
            logger.error(f"Failed to close the AzureDevOpsClient session: {e}")

    async def get_projects(self):
        if self.projects_cache and self.projects_cache_expiry > datetime.utcnow():
            return self.projects_cache
        url = f'{self.base_url}/_apis/projects?api-version=6.0'
        try:
            async with self.session.get(url, auth=self.auth) as response:
                response.raise_for_status()
                data = await response.json()
                self.projects_cache = data
                self.projects_cache_expiry = datetime.utcnow() + timedelta(minutes=10)
                logger.info("Fetched projects successfully.")
                return data
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"Failed to get projects: {e}")
            return {}

    async def get_pipelines(self, project_id):
        if project_id in self.pipelines_cache and self.pipelines_cache_expiry.get(project_id, datetime.min) > datetime.utcnow():
            return self.pipelines_cache[project_id]
        url = f'{self.base_url}/{project_id}/_apis/pipelines?api-version=6.0'
        try:
            async with self.session.get(url, auth=self.auth) as response:
                response.raise_for_status()
                data = await response.json()
                self.pipelines_cache[project_id] = data
                self.pipelines_cache_expiry[project_id] = datetime.utcnow() + timedelta(minutes=10)
                logger.info(f"Fetched pipelines for project {project_id} successfully.")
                return data
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"Failed to get pipelines for project {project_id}: {e}")
            return {}

    async def get_build_status(self, project_id, pipeline_id):
        url = f'{self.base_url}/{project_id}/_apis/build/builds?definitions={pipeline_id}&$top=10&api-version=6.0'
        try:
            async with self.session.get(url, auth=self.auth) as response:
                response.raise_for_status()
                data = await response.json()
                logger.info(f"Fetched build status for pipeline {pipeline_id} successfully.")
                return data
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"Failed to get build status: {e}")
            return {}

    async def get_all_builds(self, project_id):
        url = f'{self.base_url}/{project_id}/_apis/build/builds?$top=50&api-version=6.0'
        try:
            async with self.session.get(url, auth=self.auth) as response:
                response.raise_for_status()
                data = await response.json()
                logger.info(f"Fetched all builds for project {project_id} successfully.")
                return data
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"Failed to get all builds for project {project_id}: {e}")
            return {}

    async def trigger_pipeline(self, project_id, pipeline_id, branch):
        url = f'{self.base_url}/{project_id}/_apis/pipelines/{pipeline_id}/runs?api-version=6.0-preview.1'
        json_data = {
            "resources": {
                "repositories": {
                    "self": {
                        "refName": f"refs/heads/{branch}"
                    }
                }
            }
        }
        try:
            async with self.session.post(url, json=json_data, auth=self.auth) as response:
                response.raise_for_status()
                logger.info(f"Triggered pipeline {pipeline_id} on branch '{branch}'")
        except asyncio.CancelledError:
            raise  # Re-raise to allow task cancellation
        except Exception as e:
            logger.error(f"Failed to trigger pipeline {pipeline_id}: {e}")
            raise  # Optionally re-raise or handle as needed

    async def get_pipeline_runs(self, project_id, pipeline_id):
        url = f'{self.base_url}/{project_id}/_apis/pipelines/{pipeline_id}/runs?api-version=6.0-preview.1'
        try:
            async with self.session.get(url, auth=self.auth) as response:
                response.raise_for_status()
                data = await response.json()
                logger.info(f"Fetched pipeline runs for pipeline {pipeline_id} successfully.")
                return data
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"Failed to get pipeline runs: {e}")
            return {}

    async def cancel_build(self, project_id, build_id):
        url = f'{self.base_url}/{project_id}/_apis/build/builds/{build_id}?api-version=6.0'
        json_data = {
            "status": "Cancelling"
        }
        try:
            async with self.session.patch(url, json=json_data, auth=self.auth) as response:
                response.raise_for_status()
                logger.info(f"Cancelled build {build_id} in project {project_id}")
        except asyncio.CancelledError:
            raise  # Re-raise to allow task cancellation
        except Exception as e:
            logger.error(f"Failed to cancel build {build_id}: {e}")
            raise  # Optionally re-raise or handle as needed
