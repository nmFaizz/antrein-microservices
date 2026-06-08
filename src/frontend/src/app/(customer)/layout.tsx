import { CartProvider } from "@/components/ui/cart-provider";
import { CustomerBottomNav } from "@/components/ui/customer-bottom-nav";
import { CustomerHeader } from "@/components/ui/customer-header";

export default function CustomerLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <CartProvider>
      <div className="flex min-h-screen flex-col">
        <CustomerHeader />
        <main className="flex-1 pb-16">{children}</main>
        <CustomerBottomNav />
      </div>
    </CartProvider>
  );
}
