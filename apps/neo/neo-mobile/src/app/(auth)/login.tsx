import { useAuth } from "@/context/auth/context";
import * as WebBrowser from 'expo-web-browser';
import { Page } from "@/components/ui/page/Page";
import { Card } from "@/components/ui/card";
import React from "react";
import { Heading } from "@/components/ui/heading";
import { Button, ButtonText } from "@/components/ui/button";

WebBrowser.maybeCompleteAuthSession();

export default function Login() {
  const { login } = useAuth();

  return (
    <Page className="flex-1 items-center justify-center">
      <Card>
        <Heading size="md" className="mb-1">
          Login to Neo
        </Heading>
        <Button

          onPress={login}
        >
          <ButtonText>Login with Neo</ButtonText>
        </Button>
      </Card>
    </Page>
  );
}
