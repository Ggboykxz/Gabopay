import { View, Text, FlatList, StyleSheet } from 'react-native'

const transactions = [
  { id: '1', amount: '15,000 XAF', status: 'success', method: 'Airtel', date: 'Today, 10:30 AM' },
  { id: '2', amount: '8,500 XAF', status: 'success', method: 'Moov', date: 'Today, 9:15 AM' },
  { id: '3', amount: '25,000 XAF', status: 'failed', method: 'Card', date: 'Yesterday' },
  { id: '4', amount: '5,000 XAF', status: 'pending', method: 'Airtel', date: 'Yesterday' },
  { id: '5', amount: '12,000 XAF', status: 'success', method: 'Moov', date: 'May 5' },
]

export default function TransactionsScreen() {
  return (
    <View style={styles.container}>
      <FlatList
        data={transactions}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View style={styles.item}>
            <View style={styles.left}>
              <Text style={styles.amount}>{item.amount}</Text>
              <Text style={styles.method}>{item.method} • {item.date}</Text>
            </View>
            <Text style={[styles.status, item.status === 'success' ? styles.success : item.status === 'failed' ? styles.failed : styles.pending]}>
              {item.status}
            </Text>
          </View>
        )}
      />
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  item: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#fff',
    marginHorizontal: 16,
    marginTop: 8,
    borderRadius: 8,
    padding: 16,
  },
  left: {
    flex: 1,
  },
  amount: {
    fontSize: 16,
    fontWeight: '600',
  },
  method: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  status: {
    fontSize: 12,
    fontWeight: '500',
    textTransform: 'capitalize',
  },
  success: {
    color: '#16a34a',
  },
  failed: {
    color: '#dc2626',
  },
  pending: {
    color: '#ca8a04',
  },
})