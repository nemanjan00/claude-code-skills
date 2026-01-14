---
name: implement-js
description: Implement JavaScript code based on user requirements.
---

When implementing JavaScript code, follow these guidelines.

## Code format guide:

 * Use tabs and double quotes for strings

 * Use Common.JS syntax for imports and exports

 * I do not like to use this format `const { recordEvent } = require("./event-log");`, instead, do this `const recordEvent = require("./event-log").recordEvent;`

 * Write exports directly in `module.exports = {};`

## Project structure

 * Make sure to always create folder for each module, and create index.js inside, it helps with organization and reduces chance of conflict

## Technical guidelines

 * Use Promise instead of async/await for asynchronous operations

 * Avoid using ES6+ features that are not widely supported in Node.js environments

 * I like functional JS, map/reduce/foreach/filter should be preferred over for loops

 * I like to use wrappers for repeating code, like rate limiting, cachine, etc.

## Architectural guidelines

 * Try to encapsulate complex logic in modules and expose logic so that final code looks almost like pseudocode

 * Name modules based off their functionality, not how they are implemented (for example, module for logging stuff to mongo should be called logger, not mongo)

## Libraries and tools

 * Lib I like to use for rate limiting (how many calls of method should happen at the same time) is queue-promised

    * Install it, package name is `queue-promised`

    * Import method `wrapper` from `queue-promised` (`const wrapper = require("queue-promised").wrapper;`)

    * Use it like this `const limitedFunction = wrapper(originalFunction, 5);` where 5 is how many calls can happen at the same time

 * I like to use `uuid` package for generating uuids. I like to use `v4` method from it. and I import it like this: `const uuid = require("uuid").v4;`

## Claude notice

 * Add note to CLAUDE.md that this skill should be always used

 * Suggest changes to this skill, when I suggest code style changes

 * Try to keep CLAUDE.md in sync with project changes
