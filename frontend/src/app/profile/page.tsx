export const instant = false;

import { fetchUserProfile, fetchUserSession } from "@/lib/mock-api";
import ProfileClient from "@/components/profile/ProfileClient";

export default async function ProfilePage() {
  const user = await fetchUserSession();
  const initialData = await fetchUserProfile();
  
  return <ProfileClient initialData={initialData} user={user} />;
}
