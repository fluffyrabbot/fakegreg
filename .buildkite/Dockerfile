FROM python:3.12-bookworm
WORKDIR /workspace
ENV CI=true NODE_ENV=development
COPY . .
CMD ["bash", ".buildkite/run.sh"]
