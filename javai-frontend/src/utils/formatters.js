// Μορφοποίηση εκφώνησηςnαν το AI ξέχασε να βάλει αλλαγές γραμμής
export const formatPromptText = (text) => {
    if (!text) return "";
    return text
        .replace(/(\d+\.\s\*\*)/g, '\n\n$1') 
        .replace(/([^\n])\s*```java\s*/g, '$1\n\n```java\n');
};        

// Μορφοποίηση κώδικα Java αν το AI τον έστειλε σε μία γραμμή
export const formatJavaCode = (code) => {
    if (!code) return "";
    if (code.includes('\n')) return code;
    return code.replace(/\s{4,}/g, '\n    ');
};