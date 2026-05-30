---
name: mastra
description: |
  TypeScript framework for building production AI agents, workflows, and RAG pipelines. Use this skill whenever the user wants to build with Mastra — including creating agents, defining workflow steps, configuring memory, setting up RAG pipelines, adding observability/evals, deploying to server, or integrating with Next.js/SvelteKit/Hono. Trigger also for questions about Mastra concepts (agents vs workflows, memory scopes, step control flow, structured output, MCP servers), debugging Mastra errors, or scaffolding a new Mastra project. If the user mentions "Mastra", "mastra.ai", "@mastra/core", "createWorkflow", "createStep", or "Agent class", use this skill immediately.
---

# Mastra Skill

Mastra is an opinionated **TypeScript** framework for building AI-powered applications. It wraps the Vercel AI SDK and adds agents, workflows, memory, RAG, evals, observability, and a local Studio UI.

## Quick mental model

| Primitive  | When to use |
|------------|-------------|
| **Agent**  | Open-ended task; steps not known in advance; LLM decides |
| **Workflow** | Predetermined multi-step process; explicit control flow needed |
| **Tool**   | Reusable function an agent or workflow step can call |
| **Memory** | Persist conversation context across turns |
| **RAG**    | Ground LLM responses in your own data |
| **Scorer** | Evaluate and monitor agent/workflow output quality |

---

## 1. Project Setup

```bash
npm create mastra@latest          # scaffolds src/mastra/
```

**Canonical structure:**
```
src/mastra/
├── agents/        # Agent definitions
├── tools/         # Reusable tool functions
├── workflows/     # Workflow definitions
├── scorers/       # Eval scorers (optional)
└── index.ts       # Mastra instance — single source of truth
```

**`src/mastra/index.ts` (central registry):**
```ts
import { Mastra } from '@mastra/core'
import { LibSQLStore } from '@mastra/libsql'
import { myAgent } from './agents/my-agent'
import { myWorkflow } from './workflows/my-workflow'

export const mastra = new Mastra({
  agents: { myAgent },
  workflows: { myWorkflow },
  storage: new LibSQLStore({ id: 'store', url: 'file:./mastra.db' }),
})
```

> Always register agents and workflows in the Mastra instance. Accessing via `mastra.getAgentById()` / `mastra.getWorkflow()` gives shared storage, logging, and type inference.

---

## 2. Agents

```ts
import { Agent } from '@mastra/core/agent'

export const myAgent = new Agent({
  id: 'my-agent',
  name: 'My Agent',
  instructions: 'You are a helpful assistant.',
  model: 'openai/gpt-4o-mini',   // provider/model-name (model router)
  tools: { myTool },              // optional
  memory: new Memory({ ... }),    // optional
})
```

**Calling an agent:**
```ts
const agent = mastra.getAgentById('my-agent')

// Full response (awaits all tool calls)
const res = await agent.generate('Help me organize my day')
console.log(res.text)

// Streaming
const stream = await agent.stream('...')
for await (const chunk of stream.textStream) { ... }
```

**Structured output:**
```ts
const res = await agent.generate('Extract data', {
  output: z.object({ name: z.string(), age: z.number() }),
})
// res.object is typed
```

**Key agent options:** `id`, `name`, `instructions`, `model`, `tools`, `memory`, `scorers`, `guardrails`, `processors`

---

## 3. Workflows

Use `createStep` + `createWorkflow`. Always call `.commit()` to finalize.

```ts
import { createStep, createWorkflow } from '@mastra/core/workflows'
import { z } from 'zod'

const step1 = createStep({
  id: 'step-1',
  inputSchema: z.object({ message: z.string() }),
  outputSchema: z.object({ formatted: z.string() }),
  execute: async ({ inputData }) => ({
    formatted: inputData.message.toUpperCase(),
  }),
})

export const myWorkflow = createWorkflow({
  id: 'my-workflow',
  inputSchema: z.object({ message: z.string() }),
  outputSchema: z.object({ formatted: z.string() }),
})
  .then(step1)
  .commit()
```

**Running a workflow:**
```ts
const wf = mastra.getWorkflow('myWorkflow')
const run = await wf.createRun()
const result = await run.start({ inputData: { message: 'hello' } })

if (result.status === 'success') console.log(result.result)
```

**Result status values:** `success | failed | suspended | tripwire | paused`

### Control flow

| Method | Behaviour |
|--------|-----------|
| `.then(step)` | Sequential |
| `.parallel([step1, step2])` | Run in parallel, merge outputs |
| `.branch([{ condition, step }])` | Conditional branching |
| `.map(step)` | Fan-out over array items |

### Shared state across steps

```ts
const step = createStep({
  stateSchema: z.object({ counter: z.number() }),
  execute: async ({ state, setState }) => {
    setState({ counter: state.counter + 1 })
    return { ... }
  },
})
```

### Suspend / Resume (human-in-the-loop)

```ts
// Inside a step:
const approval = await context.suspend({ message: 'Approve?' })
// Resumes when run.resume({ stepId: 'step-id', resumeData: { approved: true } }) is called
```

---

## 4. Memory

Install: `npm install @mastra/memory @mastra/libsql`

```ts
import { Memory } from '@mastra/memory'

const agent = new Agent({
  memory: new Memory({ options: { lastMessages: 20 } }),
})

// Passing identifiers at call time:
await agent.generate('Remember my favorite color is blue.', {
  memory: { resource: 'user-123', thread: 'session-abc' },
})
```

**Memory types:**
- `lastMessages` — sliding window of recent messages (default)
- `observationalMemory: true` — background agents compress history (recommended for long sessions)
- `workingMemory` — persistent structured user data (name, prefs, goals)
- `semanticRecall` — vector-based retrieval of past messages

**Memory scopes:** `resource` (user-level, shared across threads) vs `thread` (conversation-level).

---

## 5. Tools

```ts
import { createTool } from '@mastra/core/tools'

export const myTool = createTool({
  id: 'my-tool',
  description: 'What this tool does',
  inputSchema: z.object({ query: z.string() }),
  outputSchema: z.object({ result: z.string() }),
  execute: async ({ context }) => {
    // context.query is typed
    return { result: 'done' }
  },
})
```

Register tools in the agent or pass directly. Agents can also call other agents as tools via `supervisor-agents`.

---

## 6. RAG

Install: `npm install @mastra/rag @mastra/pg`

```ts
import { MDocument } from '@mastra/rag'
import { embedMany } from 'ai'
import { ModelRouterEmbeddingModel } from '@mastra/core/llm'
import { PgVector } from '@mastra/pg'

// 1. Chunk
const doc = MDocument.fromText('Your text...')
const chunks = await doc.chunk({ strategy: 'recursive', size: 512, overlap: 50 })

// 2. Embed
const { embeddings } = await embedMany({
  values: chunks.map(c => c.text),
  model: new ModelRouterEmbeddingModel('openai/text-embedding-3-small'),
})

// 3. Store
const pgVector = new PgVector({ id: 'pg', connectionString: process.env.POSTGRES_URL })
await pgVector.upsert({ indexName: 'embeddings', vectors: embeddings })

// 4. Query
const results = await pgVector.query({ indexName: 'embeddings', queryVector, topK: 3 })
```

**Chunking strategies:** `recursive` (default), `sliding-window`, `sentence`, `markdown`, `html`
**Vector stores:** pgvector, Pinecone, Qdrant, MongoDB, LibSQL

---

## 7. Observability

```ts
import { Observability, DefaultExporter } from '@mastra/observability'

export const mastra = new Mastra({
  observability: new Observability({
    configs: {
      default: {
        serviceName: 'my-app',
        exporters: [new DefaultExporter()],
      },
    },
  }),
})
```

Traces → spans for every agent run, workflow step, tool call, and LLM request.
Metrics (duration, tokens, cost) are extracted automatically from traces.
External providers: Langfuse, Datadog, any OpenTelemetry-compatible platform.

---

## 8. Evals (Scorers)

```ts
import { createAnswerRelevancyScorer } from '@mastra/evals/scorers/prebuilt'

const agent = new Agent({
  scorers: {
    relevancy: {
      scorer: createAnswerRelevancyScorer({ model: 'openai/gpt-4o-mini' }),
      sampling: { type: 'ratio', rate: 0.5 }, // score 50% of responses
    },
  },
})
```

Scorers run asynchronously (non-blocking). Results stored in `mastra_scorers` table.
Run scorers in CI with `@mastra/evals` test runner.

---

## 9. Deployment

```bash
npm run build    # compiles to .build/
npm run start    # starts Mastra server (Express-compatible)
```

Mastra exposes a REST API automatically for each registered agent and workflow.
Supports deployment to: Vercel, Cloudflare Workers, AWS Lambda, Docker, Inngest (workflow runner).

**Server adapters:** `@mastra/server-express`, `@mastra/server-hono`, `@mastra/server-cloudflare`

---

## 10. MCP (Model Context Protocol)

Mastra can act as an MCP server, exposing tools to external agents.

```ts
import { MCPServer } from '@mastra/mcp'

const server = new MCPServer({
  name: 'my-mcp-server',
  version: '1.0.0',
  tools: { myTool },
})
```

---

## Common pitfalls

| Pitfall | Fix |
|---------|-----|
| Direct import of agent/workflow instead of `mastra.getAgentById()` | Use registry methods to get shared services |
| Forgetting `.commit()` on workflow | Always end workflow chain with `.commit()` |
| Using same `threadId` for different users | `threadId` owner (`resourceId`) is immutable after creation |
| Skipping `inputSchema`/`outputSchema` on steps | Zod schemas required for type inference and runtime validation |
| Using Workflow when Agent would suffice | Workflows = deterministic steps; Agents = dynamic reasoning |
| No storage provider when using Memory | Memory requires a storage backend (`@mastra/libsql` minimum) |

---

## Reference links

- Docs: https://mastra.ai/docs
- Agents: https://mastra.ai/docs/agents/overview
- Workflows: https://mastra.ai/docs/workflows/overview
- Memory: https://mastra.ai/docs/memory/overview
- RAG: https://mastra.ai/docs/rag/overview
- Evals: https://mastra.ai/docs/evals/overview
- Observability: https://mastra.ai/docs/observability/overview
- Reference API: https://mastra.ai/reference
- Model router: https://mastra.ai/models
- llms.txt (machine-readable): https://mastra.ai/docs/llms.txt
