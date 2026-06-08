#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Written by: mistic100
    Date:       June 8th, 2026

    Copyright:
        Copyright (C) 2026 Damien Sorel

        This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
        Public License as published by the Free Software Foundation, version 3.

        This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
        implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
        for more details.

        You should have received a copy of the GNU General Public License along with this program.
        If not, see <https://www.gnu.org/licenses/>.

"""
import logging
import requests
from typing import cast
from pathlib import Path
from unmanic.libs.unplugins.settings import PluginSettings

logger = logging.getLogger("Unmanic.Plugin.notify_tubearchivist")


class Settings(PluginSettings):
    settings = {
        "Tube Archivist URL": "http://",
        "Tube Archivist API Token": "",
    }

def notify_ta(ta_url: str, ta_token: str, video_ids: list[str]):
    headers = {
        "Authorization": f"Token {ta_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "video": video_ids
    }

    try:
        r = requests.post(f"{ta_url}/api/refresh/", json=payload, headers=headers, timeout=10)

        if r.status_code == 200:
            logger.info(f"Successfully triggered Tube Archivist refresh for {video_ids}.")
        else:
            logger.error(f"Failed to trigger Tube Archivist refresh for {video_ids}. Status code: {r.status_code}, Response: {r.text}.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error connecting to Tube Archivist API: {e}.")

def on_postprocessor_task_results(data: dict):
    if not data.get('destination_files'):
        logger.info('No destination files')
        return data

    if data.get('library_id'):
        settings = Settings(library_id=data.get('library_id'))
    else:
        settings = Settings()

    ta_url = cast(str, settings.get_setting('Tube Archivist URL'))
    ta_token = cast(str, settings.get_setting('Tube Archivist API Token'))

    if not ta_url or not ta_token:
        logger.error("Tube Archivist URL/API Token is not configured.")
        return data
    
    video_ids = [Path(file).stem for file in data.get('destination_files', [])]
    notify_ta(ta_url, ta_token, video_ids)

    return data
