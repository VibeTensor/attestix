import { formatDate } from "@/lib/utils";
import Image from "next/image";
import Link from "next/link";

export default function Author({
  name,
  image,
  twitterUsername,
  updatedAt,
  imageOnly,
}: {
  name: string;
  image: string;
  twitterUsername: string;
  updatedAt?: string;
  imageOnly?: boolean;
}) {
  if (imageOnly) {
    return (
      <Image
        src={image}
        alt={name}
        width={36}
        height={36}
        className="rounded-full border border-atx-line transition-all duration-200 group-hover:brightness-90"
      />
    );
  }

  if (updatedAt) {
    return (
      <div className="flex items-center space-x-3">
        <Image
          src={image}
          alt={name}
          width={36}
          height={36}
          className="rounded-full border border-atx-line"
        />
        <div className="flex flex-col">
          <p className="text-[14px] text-atx-ink-mid">Written by {name}</p>
          <time dateTime={updatedAt} className="text-[13px] text-atx-ink-dim">
            Last updated {formatDate(updatedAt)}
          </time>
        </div>
      </div>
    );
  }

  return (
    <Link
      href={`https://twitter.com/${twitterUsername}`}
      className="group flex items-center space-x-3"
      target="_blank"
      rel="noopener noreferrer"
    >
      <Image
        src={image}
        alt={name}
        width={40}
        height={40}
        className="rounded-full border border-atx-line transition-all duration-200 group-hover:brightness-90"
      />
      <div className="flex flex-col">
        <p className="text-[15px] font-medium text-atx-ink transition-colors duration-200 group-hover:text-atx-accent">{name}</p>
        <p className="text-[13px] text-atx-ink-dim">@{twitterUsername}</p>
      </div>
    </Link>
  );
}
