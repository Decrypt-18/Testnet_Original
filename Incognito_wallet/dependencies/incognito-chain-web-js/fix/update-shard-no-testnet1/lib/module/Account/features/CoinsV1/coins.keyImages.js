import Validator from "@lib/utils/validator";

async function checkKeyImageV1({ listOutputsCoins, shardId, version }) {
  new Validator("checkKeyImageV1-listOutputsCoins", listOutputsCoins)
    .required()
    .array();
  new Validator("checkKeyImageV1-shardId", shardId)
    .required()
    .number();

  const coinsDecrypted = await this.measureAsyncFn(
    this.decryptCoins,
    "timeCheckKeyImages.timeGetDecryptCoinsV1",
    { coins: listOutputsCoins, version }
  );
  const keyImages = this.getKeyImagesBase64Encode({ coinsDecrypted });
  let unspentCoins = [];
  let spentCoins = [];
  if (keyImages.length !== 0) {
    const keyImagesStatus = (
      await this.measureAsyncFn(
        this.rpcCoinService.apiCheckKeyImages,
        "timeCheckKeyImages.timeCheckKeyImagesV1",
        {
          keyImages,
          shardId,
          version,
        }
      )
    ) || [];
    unspentCoins = coinsDecrypted?.filter(
      (coin, index) => !keyImagesStatus[index]
    );
    spentCoins = coinsDecrypted?.filter(
      (coin, index) => keyImagesStatus[index]
    );
  }
  return {
    unspentCoins,
    spentCoins,
  };
}

export default {
  checkKeyImageV1,
};
