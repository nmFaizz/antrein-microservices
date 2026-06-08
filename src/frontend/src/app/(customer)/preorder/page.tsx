"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CartIcon, CloseIcon, MinusIcon, PlusIcon } from "@/components/ui/icons";
import { useCart } from "@/components/ui/cart-provider";
import { H2, Muted } from "@/components/ui/typography";
import { formatRupiah } from "@/lib/format";
import { useCreatePreorder } from "@/features/preorder/queries";

export default function CartPage() {
  const router = useRouter();
  const { lines, total, setQuantity, remove, clear } = useCart();
  const [notes, setNotes] = useState("");
  const [submitError, setSubmitError] = useState<string | null>(null);

  const createPreorder = useCreatePreorder();

  async function handleSubmit() {
    setSubmitError(null);
    try {
      await createPreorder.mutateAsync({
        notes: notes.trim() || null,
        items: lines.map((l) => ({ menu_item_id: l.menu.id, quantity: l.quantity })),
      });
      clear();
      setNotes("");
      router.push("/preorder/history");
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "Gagal membuat pesanan");
    }
  }

  // ── Empty cart ──────────────────────────────────────────────────────────────
  if (lines.length === 0) {
    return (
      <div className="flex flex-col gap-4 px-4 py-5">
        <H2>Keranjang</H2>
        <div className="flex flex-col items-center gap-4 py-16 text-center">
          <CartIcon className="size-12 text-muted-foreground/30" />
          <Muted>Keranjang kamu kosong.</Muted>
          <div className="flex flex-col gap-2 w-full max-w-xs">
            <Link href="/menu">
              <Button className="w-full">Lihat Menu</Button>
            </Link>
            <Link href="/preorder/history">
              <Button variant="outline" className="w-full">Lihat Riwayat Pesanan</Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // ── Checkout ────────────────────────────────────────────────────────────────
  return (
    <div className="flex flex-col gap-4 px-4 py-5 pb-8">
      <H2>Keranjang</H2>

      <Card>
        <CardHeader>
          <CardTitle>Item Pesanan</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-3">
            {lines.map((line) => (
              <div key={line.menu.id} className="flex items-center justify-between gap-2">
                <div className="flex flex-1 flex-col">
                  <span className="text-sm font-medium">{line.menu.name}</span>
                  <span className="text-xs text-muted-foreground">
                    {formatRupiah(line.menu.price)} / item
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setQuantity(line.menu.id, line.quantity - 1)}
                    className="flex size-7 items-center justify-center rounded-full bg-muted transition hover:bg-accent"
                    aria-label="Kurangi"
                  >
                    <MinusIcon className="size-3.5" />
                  </button>
                  <span className="w-6 text-center text-sm font-medium">{line.quantity}</span>
                  <button
                    type="button"
                    onClick={() => setQuantity(line.menu.id, line.quantity + 1)}
                    className="flex size-7 items-center justify-center rounded-full bg-muted transition hover:bg-accent"
                    aria-label="Tambah"
                  >
                    <PlusIcon className="size-3.5" />
                  </button>
                  <button
                    type="button"
                    onClick={() => remove(line.menu.id)}
                    className="flex size-7 items-center justify-center rounded-full text-muted-foreground transition hover:bg-destructive/10 hover:text-destructive"
                    aria-label="Hapus"
                  >
                    <CloseIcon className="size-3.5" />
                  </button>
                </div>
                <span className="w-24 text-right text-sm font-semibold">
                  {formatRupiah(line.menu.price * line.quantity)}
                </span>
              </div>
            ))}
            <hr className="border-border" />
            <div className="flex items-center justify-between font-bold">
              <span>Total</span>
              <span>{formatRupiah(total)}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Catatan</CardTitle></CardHeader>
        <CardContent>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Contoh: tidak pakai pedas, tanpa bawang…"
            rows={3}
            className="w-full resize-none rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </CardContent>
      </Card>

      {submitError && (
        <p className="text-sm text-destructive">{submitError}</p>
      )}

      <Button
        size="lg"
        className="w-full"
        onClick={handleSubmit}
        disabled={createPreorder.isPending}
      >
        {createPreorder.isPending ? "Memproses…" : "Buat Pesanan"}
      </Button>
    </div>
  );
}
