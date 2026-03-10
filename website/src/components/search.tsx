"use client";

import type { SharedProps } from "fumadocs-ui/components/dialog/search";
import DefaultSearchDialog from "fumadocs-ui/components/dialog/search-default";

export default function SearchDialog(props: SharedProps) {
	return <DefaultSearchDialog {...props} type="static" />;
}
