import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const skillName = 'miniapp-game-offline';
const entry = new URL('./skills/miniapp-game-offline/SKILL.md', import.meta.url);

export const name = 'miniapp-game-offline';
export const inject = ['skills'];

export function apply(ctx) {
  const raw = readFileSync(entry, 'utf8');
  // The bundled skill keeps its name and description as single-line fields.
  const frontmatter = /^---\r?\nname: ([a-z0-9-]+)\r?\ndescription: ([^\r\n]+)\r?\n---(?:\r?\n|$)/u.exec(raw);
  if (!frontmatter || frontmatter[1] !== skillName) {
    throw new Error('miniapp-game-offline: invalid packaged skill frontmatter');
  }
  ctx.skills.register({
    name: skillName,
    description: frontmatter[2],
    content: raw.slice(frontmatter[0].length).trim(),
    path: fileURLToPath(entry),
    source: 'bundled',
    provider: name,
    resourceBase: { kind: 'directory', path: fileURLToPath(new URL('.', entry)) },
  });
}
