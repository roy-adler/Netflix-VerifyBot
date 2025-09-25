#!/usr/bin/env python3
"""
Netflix VerifyBot - Main Entry Point

This is the main entry point for the Netflix VerifyBot application.
It uses the new modular architecture for better maintainability and structure.

The application monitors an email inbox for Netflix verification emails
and automatically processes them by clicking verification links and
extracting verification codes.
"""

import asyncio
import sys
from app import main

if __name__ == "__main__":
    asyncio.run(main())