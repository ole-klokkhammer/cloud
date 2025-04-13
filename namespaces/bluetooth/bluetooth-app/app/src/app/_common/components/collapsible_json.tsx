"use client";

import { useState } from "react";
import {
    Box,
    Button,
    Collapse,
    Typography
} from "@mui/material";
import { ExpandLess, ExpandMore } from "@mui/icons-material";

export const CollapsibleJson = ({ data }: { data: any }) => {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <Box>
            <Button
                size="small"
                onClick={() => setIsOpen(!isOpen)}
                startIcon={isOpen ? <ExpandLess /> : <ExpandMore />}
            >
                {isOpen ? "Collapse" : "Expand"}
            </Button>
            <Collapse in={isOpen} timeout="auto" unmountOnExit>
                <Box sx={{ ml: 2 }}>
                    {Object.entries(data).map(([key, value]) => (
                        <Box key={key} sx={{ mb: 1 }}>
                            <Typography variant="body2">
                                <strong>{key}:</strong>{" "}
                                {typeof value === "object" && value !== null ? (
                                    <CollapsibleJson data={value} />
                                ) : (
                                    JSON.stringify(value)
                                )}
                            </Typography>
                        </Box>
                    ))}
                </Box>
            </Collapse>
        </Box>
    );
};