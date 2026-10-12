import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'
import ts from 'typescript'

const source = readFileSync(new URL('../src/lib/blog.ts', import.meta.url), 'utf8')
const compiled = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 },
}).outputText.replace(/from\s+["']([^"']+)["']/g, (_, specifier) => `from ${JSON.stringify(import.meta.resolve(specifier))}`)
const { markdownToHTML } = await import(`data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}`)

test('heading IDs use decoded text and remain unique across duplicates', async () => {
  const html = await markdownToHTML('## **Evidence** & `keys`\n\n## Evidence & keys')
  assert.match(html, /<h2 id="evidence-keys">/)
  assert.match(html, /<h2 id="evidence-keys-2">/)
})

test('malformed raw heading markup cannot become a script element', async () => {
  const html = await markdownToHTML('## <script<script>>alert(1)</script>\n\n## Escaped &lt;script&gt;')
  assert.doesNotMatch(html, /<script\b/i)
  assert.match(html, /<h2 id="escaped-script">/)
})

test('existing suffixed headings cannot collide with duplicate heading IDs', async () => {
  const html = await markdownToHTML('## Foo\n\n## Foo-3\n\n## Foo')
  const ids = [...html.matchAll(/<h2 id="([^"]+)">/g)].map((match) => match[1])
  assert.equal(ids.length, 3)
  assert.equal(new Set(ids).size, 3)
})
