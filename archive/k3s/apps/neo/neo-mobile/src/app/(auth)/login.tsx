import { useAuth } from "@/context/auth/context";
import * as WebBrowser from 'expo-web-browser'; 
import { Card } from "@/components/ui/card";
import React from "react";
import { Heading } from "@/components/ui/heading";
import { Button, ButtonText } from "@/components/ui/button";
import { Box } from "@/components/ui/box";

WebBrowser.maybeCompleteAuthSession();

export default function Login() {
  const { login } = useAuth();

  return (
    <Box className="flex-1 items-center justify-center">
      <Card>
        <Heading size="md" className="mb-1">
          Welcome to Neo
        </Heading>
        <Button onPress={login}>
          <ButtonText>Login</ButtonText>
        </Button>
      </Card>
    </Box>
  );
}
