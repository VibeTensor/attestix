import { copyFileSync, existsSync, mkdirSync, readFileSync, readdirSync, renameSync, writeFileSync } from 'node:fs'
import { randomUUID } from 'node:crypto'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const BEGIN = '# BEGIN ATTESTIX BLOG REDIRECTS'
const END = '# END ATTESTIX BLOG REDIRECTS'

export function blogRedirects(slugs) {
  for (const slug of slugs) {
    if (typeof slug !== 'string' || !/^[a-z0-9-]+$/.test(slug)) {
      throw new Error('Invalid blog redirect slug')
    }
  }

  return [
    BEGIN,
    '# Recover article links shared after a failed static RSC navigation.',
    '/blog.txt /blog 301',
    ...[...new Set(slugs)].sort().map((slug) => `/blog/${slug}.txt /blog/${slug} 301`),
    END,
    '',
  ].join('\n')
}

export function generateBlogRedirects(root) {
  const slugs = readdirSync(join(root, 'content'), { withFileTypes: true })
    .filter((entry) => entry.isFile() && entry.name.endsWith('.mdx'))
    .map((entry) => entry.name.slice(0, -4))
  const destination = join(root, 'public', '_redirects')
  const block = blogRedirects(slugs)
  let content = block

  if (existsSync(destination)) {
    const previous = readFileSync(destination, 'utf8')
    const start = previous.indexOf(BEGIN)
    const end = previous.indexOf(END)
    if (start < 0 && end < 0) {
      content = `${previous.trimEnd()}\n\n${block}`
    } else {
      if (start < 0 || end < start || previous.indexOf(BEGIN, start + BEGIN.length) >= 0 || previous.indexOf(END, end + END.length) >= 0) {
        throw new Error('Ambiguous managed blog redirect block')
      }
      content = `${previous.slice(0, start)}${block.trimEnd()}${previous.slice(end + END.length)}`
    }
    if (previous === content) return slugs.length
    const backupDirectory = join(root, '.source', 'blog-redirect-backups')
    mkdirSync(backupDirectory, { recursive: true })
    const backup = join(backupDirectory, `${Date.now()}-${randomUUID()}.txt`)
    copyFileSync(destination, backup)
    if (!readFileSync(destination).equals(readFileSync(backup))) {
      throw new Error('Blog redirect backup verification failed')
    }
  }

  mkdirSync(dirname(destination), { recursive: true })
  const temporary = `${destination}.${randomUUID()}.tmp`
  writeFileSync(temporary, content)
  renameSync(temporary, destination)
  return slugs.length
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
  console.log(`Generated canonical redirects for ${generateBlogRedirects(root)} blog articles`)
}
