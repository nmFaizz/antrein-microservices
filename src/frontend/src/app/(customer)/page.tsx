"use client";

import Link from "next/link";

import { Button } from "@/components/ui/button";
import { MenuBookIcon } from "@/components/ui/icons";
import { H1, Lead, Muted } from "@/components/ui/typography";

export default function CustomerHome() {
  return (
    <div className="flex min-h-[80vh] flex-col items-center justify-center gap-6 px-6 text-center">
      <span className="flex size-20 items-center justify-center rounded-2xl bg-primary text-primary-foreground">
        <MenuBookIcon className="size-10" />
      </span>
      <div className="flex flex-col gap-2">
        <H1>Selamat Datang di AntreIn</H1>
        <Lead>Pesan makanan favoritmu tanpa antri panjang.</Lead>
        <Muted>
          Pilih menu, pesan, dan dapatkan notifikasi saat pesananmu siap.
        </Muted>
      </div>
      <Link href="/menu">
        <Button size="lg">Lihat Menu</Button>
      </Link>
    </div>
  );
}
