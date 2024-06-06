import logging

from aiogram.types import CallbackQuery
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from .filters import SpecialRegisterFilter, RequireAdmin, RequireRegistration
from aiogram.types import Message
from validators import is_user_registered
from commands import StartCallbackQueryCommands as StartCQC
from db import add_user_to_bot
import asyncio






