"use server";

import { Box, Container, Typography } from "@mui/material";
import NextLink from 'next/link';
import Link from '@mui/material/Link';

export default async function Home() {
  return (
    <Container maxWidth="lg">
      <Box
        sx={{
          my: 4,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        <Typography variant="h4" component="h1" sx={{ mb: 2 }}>
          Material UI - Next.js App Router example in TypeScript
        </Typography>
        <Link href="/bluetooth/scan" color="secondary" component={NextLink}>
          Go to the bluetooth scan
        </Link>

      </Box>
    </Container>
  );
}
