---
name: implement-js
description: Implement JavaScript code based on user requirements.
---

When implementing JavaScript code:

 * Use Common.JS syntax for imports and exports

 * Make sure to always create folder for each module, and create index.js inside, it helps with organization and reduces chance of conflict

 * Write exports directly in `module.exports = {};`

 * Use Promise instead of async/await for asynchronous operations

 * Avoid using ES6+ features that are not widely supported in Node.js environments

 * Try to encapsulate complex logic in modules and expose logic so that final code looks almost like pseudocode

 * Name modules based off their functionality, not how they are implemented (for example, module for logging stuff to mongo should be called logger, not mongo)

 * Add note to CLAUDE.md that this skill should be always used
