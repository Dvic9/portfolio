<?php
require 'vendor/autoload.php';
// teste transformar xml em danfe em massa
use NFePHP\DA\NFe\Danfe;

$inputDir = __DIR__ . '/xmls_nfes';
$outputDir = __DIR__ . '/danfes';

if (!is_dir($outputDir)) {
    mkdir($outputDir, 0777, true);
}
    
$files = glob($inputDir . '/*.xml');

foreach ($files as $xmlFile) {
    try {
        $xml = file_get_contents($xmlFile);

        // Cria o DANFE
        $danfe = new Danfe($xml);

        // Monta o DANFE (gera o PDF internamente)
        $danfe->monta(); // você pode passar parâmetros se quiser alterar papel/orientação

        // Renderiza e retorna o PDF como string
        $pdfContent = $danfe->render();

        // Salva o PDF em disco
        $filename = $outputDir . '/' . basename($xmlFile, '.xml') . '.pdf';
        file_put_contents($filename, $pdfContent);

        echo "✅ DANFE gerado: " . basename($filename) . PHP_EOL;

    } catch (\Exception $e) {
        echo "❌ Erro ao gerar DANFE para " . basename($xmlFile) . ": " . $e->getMessage() . PHP_EOL;
    }
}
