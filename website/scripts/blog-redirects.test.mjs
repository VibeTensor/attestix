import assert from 'node:assert/strict'
import { mkdirSync, mkdtempSync, readFileSync, readdirSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import test from 'node:test'
import { blogRedirects, generateBlogRedirects } from './generate-blog-redirects.mjs'

test('every published article has an explicit permanent redirect to its human URL', () => {
  const slugs = readdirSync(new URL('../content/', import.meta.url))
    .filter((name) => name.endsWith('.mdx'))
    .map((name) => name.slice(0, -4))
  const rules = blogRedirects(slugs).split('\n')
  assert.ok(slugs.length > 0)
  for (const slug of slugs) {
    assert.ok(rules.includes(`/blog/${slug}.txt /blog/${slug} 301`))
  }
  assert.ok(rules.includes('/blog.txt /blog 301'))
  assert.ok(!rules.some((rule) => rule.includes('*')))
})

test('new content is discovered while docs and unrelated text exports stay untouched', () => {
  const root = mkdtempSync(join(tmpdir(), 'attestix-blog-redirects-'))
  mkdirSync(join(root, 'content', 'docs'), { recursive: true })
  mkdirSync(join(root, 'public'))
  writeFileSync(join(root, 'content', 'new-release.mdx'), '# New release')
  writeFileSync(join(root, 'content', 'docs', 'quickstart.mdx'), '# Docs')
  writeFileSync(join(root, 'public', 'llms.txt'), 'Agent documentation')
  assert.equal(generateBlogRedirects(root), 1)
  const rules = readFileSync(join(root, 'public', '_redirects'), 'utf8')
  assert.match(rules, /\/blog\/new-release\.txt \/blog\/new-release 301/)
  assert.doesNotMatch(rules, /quickstart|llms/)
  assert.equal(readFileSync(join(root, 'public', 'llms.txt'), 'utf8'), 'Agent documentation')
})

test('existing redirect content is preserved byte for byte before regeneration', () => {
  const root = mkdtempSync(join(tmpdir(), 'attestix-blog-backup-'))
  mkdirSync(join(root, 'content'))
  mkdirSync(join(root, 'public'))
  const previous = Buffer.from('/previous /destination 301\n')
  writeFileSync(join(root, 'public', '_redirects'), previous)
  generateBlogRedirects(root)
  const backups = readdirSync(join(root, '.source', 'blog-redirect-backups'))
  assert.equal(backups.length, 1)
  assert.deepEqual(readFileSync(join(root, '.source', 'blog-redirect-backups', backups[0])), previous)
  assert.match(readFileSync(join(root, 'public', '_redirects'), 'utf8'), /^\/previous \/destination 301\n/)
  generateBlogRedirects(root)
  const rules = readFileSync(join(root, 'public', '_redirects'), 'utf8')
  assert.equal(rules.split('/blog.txt /blog 301').length - 1, 1)
})

test('invalid slugs cannot inject paths or additional redirect rules', () => {
  for (const slug of ['../outside', 'post.txt', 'post\n/other /target 301', '', null]) {
    assert.throws(() => blogRedirects([slug]), /Invalid blog redirect slug/)
  }
  assert.equal(blogRedirects(['z-post', 'a-post', 'a-post']), blogRedirects(['a-post', 'z-post']))
})
