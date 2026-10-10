# Claude agent template

A template for building agents with the Claude Agent SDK: a chat in the browser, an agent on the server, one Docker image.

## Features

- **Chat.** Replies stream in as the agent writes them, and each tool call shows as it happens.
- **Docs as context.** As shipped, the agent answers questions about Ohara from Ohara's own docs, read through an Ohara MCP server. Rewrite the system prompt to build your own agent.
- **Resumable.** A reload or a restart keeps the conversation. "New chat" starts over.
- **Self-hosted.** One container, one data volume, one required variable.

## Principles

- Simple and solid by design: few moving parts, few dependencies.
- The agent only gets the tools you give it. Built-in tools are off.
- Docs live in [`docs/`](docs/README.md) and stay in sync with the code through Ohara.

## Get started

See [Development](docs/development.md) to run it, and [Architecture](docs/architecture.md) for how it works.

## Security

See [SECURITY.md](SECURITY.md) to report a vulnerability.

## License

Apache-2.0.
