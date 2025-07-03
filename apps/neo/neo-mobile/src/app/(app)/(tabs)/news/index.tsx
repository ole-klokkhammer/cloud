import { Box } from "@/components/ui/box";
import { Text } from "@/components/ui/text";
import { Image } from "react-native";


export default function HomePage() {
  return (
    <Box className="flex-1">
      <Image
        source={require('@/assets/images/neo/neo_v2.png')}
        className="w-full align-baseline self-center mb-2"
        resizeMode="cover"
      />
      <Text>Welcome to the Home Screen!</Text>
    </Box>
  );
}
