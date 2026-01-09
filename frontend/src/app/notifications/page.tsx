import { notFound } from "next/navigation";

export default function NotificationsPage() {
  // 通知はヘッダーのアイコンからページ遷移なしで表示する仕様に変更したため、
  // /notifications は 404 扱いにします。
  notFound();
}
