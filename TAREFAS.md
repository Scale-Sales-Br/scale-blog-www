# Tarefas do blog da Scale Sales

Fila de trabalho. O que está feito vive no histórico do repositório; aqui fica
o que ainda não existe.

## 1 · Carrossel de Instagram a partir do artigo do dia

**O que é:** cada artigo publicado vira um carrossel de 6 a 9 cartões para o
perfil da Scale, com a identidade do site (fundo `#120727`, Poppins no título,
Inter no corpo, acento magenta `#E457F9`).

**Por que:** o artigo já carrega o trabalho pesado, que é a apuração e a leitura
comercial da notícia. O carrossel é redistribuição, não conteúdo novo.

**Como deve funcionar:**

- Entrada: o mesmo `fonte/AAAA-MM-DD-slug.md` que gerou o artigo.
- Estrutura dos cartões: 1 gancho com o fato · 2 o número principal, com a
  ressalva de quem o declarou · 3 a 6 a leitura da Scale, uma ideia por cartão ·
  penúltimo com os passos práticos · último com o convite ao diagnóstico gratuito.
- Saída: PNG 1080×1350 por cartão, em `social/<slug>/`, mais a legenda em
  `social/<slug>/legenda.txt` com os primeiros 125 caracteres resolvendo sozinhos.
- Técnica: renderizar HTML com Playwright e capturar cada cartão, reaproveitando
  `estilo.css`. Não gerar imagem por IA: o texto sai errado e a marca escorrega.

**Decisões que faltam:** quem publica (manual pelo celular ou API do Instagram, que
exige conta comercial ligada a uma página do Facebook e passa por revisão da Meta);
e se o carrossel sai todo dia ou só quando o artigo for forte.

## 2 · Publicar o artigo como post no LinkedIn

**O que é:** o artigo do dia vira um post na página da Scale Sales no LinkedIn,
com texto próprio e link para o artigo.

**Como deve funcionar:**

- O texto do post **não** é o primeiro parágrafo do artigo. É um texto de rede:
  o fato em duas linhas, a leitura comercial em três, e a pergunta que faz comentar.
  O link vai no fim.
- Publicação pela API de Posts do LinkedIn, que exige um app aprovado e o produto
  "Community Management API", com o escopo `w_organization_social` e um token da
  página. O token da página expira em 60 dias e precisa de rotina de renovação.

**Decisões que faltam:** se o post sai pela página da Scale, pelo perfil do Alberto,
ou pelos dois com textos diferentes. O perfil pessoal costuma alcançar mais que a
página, e a API de perfil pessoal é mais restrita que a da organização.

## 3 · Publicar como novidade no Google Meu Negócio

**O que é:** o artigo vira uma publicação no perfil da Scale no Google Business
Profile, que aparece na busca pela marca e no Maps.

**Como deve funcionar:**

- Tipo `STANDARD`, com resumo de até 1.500 caracteres (os primeiros 150 são os
  que aparecem), uma imagem e o botão "Saiba mais" apontando para o artigo.
- Publicação pela Business Profile API, que exige o perfil verificado e acesso
  concedido ao projeto no Google Cloud.

**Atenção:** publicação do Google Meu Negócio **expira em 7 dias**. Se a rotina
publicar todo dia, o perfil fica sempre com conteúdo novo. Se parar, o perfil
esvazia sozinho, o que é pior que nunca ter começado.

**Decisões que faltam:** se o perfil da Scale já está verificado, e qual imagem
acompanha (o cartão de compartilhamento do artigo serve).

## Antes de qualquer uma das três

As três dependem de credencial de plataforma, e credencial não pode morar no
agente da nuvem. O caminho é o mesmo do blog: o agente gera o material e comita;
quem tem a credencial publica. Resolver isso uma vez serve para as três.
