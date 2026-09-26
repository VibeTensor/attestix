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
      className="group flex flex-col overflow-hidden rounded-2xl border border-atx-line bg-atx-panel/60 transition-colors duration-200 hover:border-atx-ink-dim"
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
      <div className="flex flex-1 flex-col gap-2 p-6">
        <time
          dateTime={data.publishedAt}
          className="text-[13px] text-atx-ink-dim"
        >
          {formatDate(data.publishedAt)}
        </time>
        <h3 className="text-[19px] font-semibold leading-[1.3] tracking-[-0.48px] text-atx-ink">
          {data.title}
        </h3>
        <p className="text-[15px] leading-[1.6] text-atx-ink-mid">
          {data.summary}
        </p>
        <div className="mt-auto pt-4 text-[14px] font-medium text-atx-ink-mid transition-colors duration-200 group-hover:text-atx-ink">
          Read article <span className="inline-block transition-transform duration-200 group-hover:translate-x-0.5">&rarr;</span>
        </div>
      </div>
    </Link>
  );
}
