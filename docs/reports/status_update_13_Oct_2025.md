# Status Report&mdash;13 October 2025

__Task:__ Investigate data sources used by  [ENV-AGENTS](https://github.com/aparkin/env-agents/tree/main)

__Overall Goal:__ Facilitate use of ENV-AGENTS (and similar) source data for research applications

## Methodology
- Use Copilot to wrap source data APIs
  - Use "adapter" approach as in ENV-AGENTS
  - Do not attempt to standardize queries or output data (as done in ENV-AGENTS)
- For each data provider:
  - Identify all available datasets (not just what is used in env-agents)
  - Assess options for automatic discovery of API (openapi, etc)
  - Document considerations relevant to KBase project
- Why this approach?
  - Don't want to write a lot of code by hand that will probably never be used again
  - Allows assessment of how useful AI agents might be for researchers attempting to use native data source APIs

## Status
- Worked through three data sources so far (NASA POWER, GBIF, OpenAQ)

## General Observations
- APIs seem stable and well-documented (all had OpenAPI specs available).
- All three have easy-to-use web portals available.
- Of the two data sources I could find estimates for (NASA POWER, GBIF), the underlying data is (very roughly) ~5-10 TB.
- It's not too hard to vibe-code your way to getting data from these APIs (definitely not for production, but potentially useful for one-off research applications).
- APIs are geared towards facilitating fine-grained searches, not doing "bulk" data transfers.
- Several of these sources are already compilations of disparate datasets that have gone through some standardization processes.
- The lowest-cost, lowest-risk, most straightforward and actionable way to use these data are through the web portals already developed by the maintainers of the datasets.
  - The value-add of any proposed development should be measured against this approach
- Bulk data transfer may require contacting the admins of the various data sources. I couldn't find anything by searching for this.

## My Rough Understanding of Potential Options (or Roadmap)

| Data Access Method                                            | User Skills                      | Throughput  | Dev Cost                                                        | User Costs                                                                                                                  | Pros                                                                                                       | Cons                                                                                                                                                                       |
|---------------------------------------------------------------|----------------------------------|-------------|-----------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Native Web Portal                                             | Browser; Excel; multiple portals | Low         | Very Low (docs)                                                 | Medium (learning to use different portals; time spent on individual searches; translation between platform concepts/naming) | Low dev cost; currently available                                                                          | Low throughput                                                                                                                                                             |
| Jupyter Notebook (Native APIs)                                | Python; AI Agent                 | Medium      | Low-Medium (tutorials; examples, user forums, workshops)        | Medium-High (learning APIs with AI assist; translation between platform concepts/naming)                                    | Low dev cost; high throughput; users gain transferable skills                                              | High spin-up time for users w/ limited coding experience; uncertain usefulness of AI agents                                                                                |
| Jupyter Notebook (custom Python pkg using native APIs)        | Python                           | Medium-High | Medium-High (pkg using multiple APIs, docs, user forums)        | Low-Medium (integrating output with various schemas/naming)                                                                 | High throughput; only one portal for users to learn                                                        | High dev cost; volatile APIs; non-transferable user skills                                                                                                                 |
| Jupyter Notebook (bulk data ingestion; standardized querying) | Python                           | High        | High (custom portal and API; data ingestion; docs; user forums) | Low (standardized query; more consistent results schemas/naming)                                                            | High throughput; only one portal for users to learn; standardized data sets; single back-end API           | High dev cost; loss of information through standardizing data; volatile source data schemas; volatile bulk transfer APIs (if even available); non-transferable user skills |

## Questions
- Can we eliminate any of the above options?
- Are there other options on the table?
- How much do we know about our target user base (skillset in particular)?
- How valuable are the transferable skills gained through training users to develop their own scripts?
- How much of these data would be used for a single research application?