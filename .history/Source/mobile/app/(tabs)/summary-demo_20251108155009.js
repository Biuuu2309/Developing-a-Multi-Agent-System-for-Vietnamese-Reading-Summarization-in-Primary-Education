import { View, Text } from 'react-native';
import { useEffect, useState } from 'react';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';

export default function SummaryDemo() {
    return (
        <ThemedView>
            <ThemedText>Summary Demo</ThemedText>
        </ThemedView>
    );
}