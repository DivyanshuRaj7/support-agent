# Tech Stack

| Layer | Choice | Why (be ready to state the alternative you rejected) |
|---|---|---|
| Orchestration | LangGraph | Explicit state machine, conditional routing, inspectable state — vs. plain LangChain agent loop, which hides routing logic inside the LLM's own reasoning |
| API gateway | FastAPI | Async-native, Pydantic validation built in, fast to stand up — vs. Flask, which needs extra libraries for the same validation/async support |
| LLM provider | OpenAI API (swappable via `LLMClient` abstraction) | Abstraction means the actual provider is a config choice, not an architecture choice — could swap to Anthropic/local model with one file changed |
| Vector store (Week 2) | Qdrant (or Chroma for local dev) | Open-source, runs locally with zero cloud cost during development — vs. Pinecone, which is fine but adds a paid dependency you don't need yet |
| Graph store (stretch — Graph RAG) | NetworkX (in-memory) | Account↔Order↔Ticket relationships at portfolio scale don't need a graph database — vs. Neo4j, which is the real-world-correct choice at scale but unjustifiable overhead for a few hundred synthetic records |
| Memory/summarization | In-house token-budget summarizer | Keeps cost flat as conversations grow — vs. just raising context window, which scales cost linearly with conversation length |
| Guardrail validation | Pydantic schemas | Already a FastAPI dependency, zero extra library — vs. a separate guardrails framework (Guardrails AI, NeMo Guardrails), which is a fair Week-3 upgrade if schema validation isn't enough |
| Observability (Week 3) | Langfuse (self-hostable) | Open-source, purpose-built for LLM traces — vs. rolling fully custom logging, which reinvents tracing |
| Eval framework (Week 3) | Custom pytest-based eval suite | Small enough scope that a full eval platform (Braintrust, etc.) is overkill for a portfolio project — say this explicitly, it shows judgment about tool selection, not just tool knowledge |
| Deployment (Week 3) | Docker + Render/Railway | Cheap, fast to demo live — vs. full Kubernetes, which is real-world correct at scale but overkill and untestable for a solo portfolio project; say this out loud in interviews, it shows you scope tools to the problem size |
| CI | GitHub Actions | Free, runs the eval suite + tests on every push |

## Note on "why not the trendiest tool"
Several rows above intentionally pick the simpler/cheaper option over a
flashier one (Chroma over Pinecone, custom evals over a platform, Render
over Kubernetes). This is deliberate: a senior engineer scoping tool choice
to actual problem size is a stronger signal than name-dropping every trendy
tool. Be ready to say this plainly if asked "why didn't you use X."
