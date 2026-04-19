import { Post } from "@/lib/blog";
import { formatDate } from "@/lib/utils";
import Image from "next/image";
import Link from "next/link";

export default function BlogCard({
  data,
  priority,
}: {
  data: Post;
  priority?: boolean;
}) {
  return (
    <Link
      href={`/blog/${data.slug}`}
      className="group flex flex-col overflow-hidden rounded-atx-md border border-atx-line-soft bg-atx-panel transition-colors hover:border-atx-accent/60 hover:bg-atx-panel-hi"
    >
      <div className="relative aspect-[16/9] w-full overflow-hidden border-b border-atx-line-soft bg-atx-bg-sunken">
        {data.image ? (
          <Image
            src={data.image}
            width={1200}
            height={630}
            alt={data.title}
            priority={priority}
            className="h-full w-full object-cover"
          />
        ) : null}
      </div>
      <div className="flex flex-1 flex-col gap-2 p-5">
        <time
          dateTime={data.publishedAt}
          className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint"
        >
          {formatDate(data.publishedAt)}
        </time>
        <h3 className="font-serif text-[22px] leading-[1.25] text-atx-ink">
          {data.title}
        </h3>
        <p className="text-[13.5px] leading-[1.55] text-atx-ink-mid">
          {data.summary}
        </p>
        <div className="mt-auto pt-4 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-accent">
          read article <span className="inline-block transition-transform group-hover:translate-x-0.5">&rarr;</span>
        </div>
      </div>
    </Link>
  );
}
