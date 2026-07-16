# Better Auth Transition

## Project status

Treat Auth.js and its former NextAuth.js name as an existing project overseen and maintained by the Better Auth team. Existing applications continue to receive security patches and urgent fixes.

## Choose a project path

Prefer Better Auth for a new project unless a current feature gap blocks the required design. A notable reason to retain Auth.js is stateless session management without a database.

For an existing Auth.js or NextAuth.js application:

1. Keep dependencies current so security and urgent fixes continue to land.
2. Inventory session, provider, adapter, and framework requirements.
3. Confirm that Better Auth supports every required behavior.
4. Use the NextAuth migration guide when moving to Better Auth.

Do not migrate solely because maintenance oversight changed; decide from application requirements and the migration cost.
