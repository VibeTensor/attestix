import { defineDocs, defineConfig } from 'fumadocs-mdx/config';
import type { Root } from 'mdast';
import { visit } from 'unist-util-visit';

/** Remark plugin: convert ```mermaid code blocks into <Mermaid chart="..." /> JSX. */
function remarkMermaid() {
	return (tree: Root) => {
		visit(tree, 'code', (node, index, parent) => {
			if (node.lang !== 'mermaid' || index == null || !parent) return;
			const escaped = node.value
				.replace(/\\/g, '\\\\')
				.replace(/`/g, '\\`')
				.replace(/\$/g, '\\$');
			parent.children.splice(index, 1, {
				type: 'mdxJsxFlowElement' as 'code',
				name: 'Mermaid',
				attributes: [
					{
						type: 'mdxJsxAttribute' as unknown as undefined,
						name: 'chart',
						value: escaped,
					} as unknown as never,
				],
				children: [],
			} as unknown as typeof node);
		});
	};
}

export const docs = defineDocs({
  dir: 'content/docs',
});

export default defineConfig({
	mdxOptions: {
		remarkPlugins: [remarkMermaid],
	},
});
