import { View, Text, TouchableOpacity, StyleSheet } from 'react-native'

export default function ScanScreen() {
  return (
    <View style={styles.container}>
      <View style={styles.scannerPlaceholder}>
        <Text style={styles.placeholderText}>QR Scanner</Text>
        <Text style={styles.placeholderSubtext}>Point camera at QR code</Text>
      </View>

      <View style={styles.form}>
        <Text style={styles.label}>Or enter amount manually</Text>
        <View style={styles.inputContainer}>
          <Text style={styles.currency}>XAF</Text>
          <Text style={styles.amount}>0</Text>
        </View>

        <TouchableOpacity style={styles.button}>
          <Text style={styles.buttonText}>Collect Payment</Text>
        </TouchableOpacity>
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scannerPlaceholder: {
    flex: 1,
    backgroundColor: '#1a1a1a',
    margin: 20,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  placeholderText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  placeholderSubtext: {
    color: '#999',
    marginTop: 8,
  },
  form: {
    backgroundColor: '#fff',
    margin: 20,
    borderRadius: 12,
    padding: 20,
  },
  label: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    marginBottom: 20,
  },
  currency: {
    fontSize: 24,
    color: '#666',
  },
  amount: {
    fontSize: 48,
    fontWeight: 'bold',
  },
  button: {
    backgroundColor: '#009e60',
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
})