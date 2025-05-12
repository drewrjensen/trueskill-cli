# ----- Stage 1: Build -----
FROM python:3-alpine AS builder
WORKDIR /app

COPY Pipfile Pipfile.lock ./
RUN pip install pipenv && pipenv install --system --deploy
RUN pip install pyinstaller && apk add --no-cache binutils

COPY . .
RUN rm -rf build __pycache__ venv *.spec
RUN pyinstaller --onefile --add-data "schemas.sql:." src/main.py

# ----- Stage 2: Runtime -----
FROM alpine:latest
WORKDIR /app

# Only copy the built binary
COPY --from=builder /app/dist/main /usr/local/bin/trueskill-cli
RUN chmod +x /usr/local/bin/trueskill-cli

# No default CMD; container acts as on-demand CLI tool