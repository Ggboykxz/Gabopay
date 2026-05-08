import { Stack } from 'expo-router'
import { StatusBar } from 'expo-status-bar'

export default function RootLayout() {
  return (
    <>
      <StatusBar style="light" />
      <Stack
        screenOptions={{
          headerStyle: {
            backgroundColor: '#111214',
          },
          headerTintColor: '#f1f3f5',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
          contentStyle: {
            backgroundColor: '#0a0b0c',
          },
        }}
      >
        <Stack.Screen 
          name="index" 
          options={{ 
            title: 'GABOPAY',
            headerShown: false,
          }} 
        />
        <Stack.Screen 
          name="dashboard" 
          options={{ 
            title: 'Dashboard',
            headerShown: false,
          }} 
        />
        <Stack.Screen 
          name="scan" 
          options={{ 
            title: 'Scan QR',
            presentation: 'modal',
          }} 
        />
        <Stack.Screen 
          name="transactions" 
          options={{ 
            title: 'Transactions',
          }} 
        />
      </Stack>
    </>
  )
}