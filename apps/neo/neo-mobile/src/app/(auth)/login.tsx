import { useAuth } from "@/context/auth/context";
import * as WebBrowser from 'expo-web-browser';
import { Button, Text } from "react-native";
import { Page } from "@/components/ui/layout/page";
import { Card } from "@/components/ui/card/card";

WebBrowser.maybeCompleteAuthSession();

export default function Login() {
  const { login } = useAuth();

  return (
    <Page className="flex-1 items-center justify-center">
      <Card header="Login to Neo">
        <Button
          title="Login"
          onPress={login}
        />
      </Card>
    </Page>
  );
}
