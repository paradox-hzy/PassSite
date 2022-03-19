<template>
  <div>
    <div class="mar-large full-width font-normal">
      <div class="mar-large">
        <p>
          &nbsp;&nbsp;&nbsp;PL模型利用PCFG的思想，根据识别规则提取口令中不同段的内容，并将每个口令转换为模板口令。例如，根据原始的PCFG规则，可以将口令“abc123@@”转换为模板口令“L3D3S2”，其中L表示字母，D表示数字，S表示特殊字符，模板口令中的数字表示该段的长度。除了矩阵是从模板口令中获得的，其余的训练过程与基于LSTM的模型基本相同。生成部分分为两个步骤，首先生成模板化的口令，然后使用所提取的内容来生成最终的口令。采用基于PCFG的预处理方法的模型被认为是片段级别的（segment-level）。
        </p>
      </div>
    </div>
    <div class="pad mar-large shadow border-radius font-normal bac">
      <div class="full-width">
        <div class="mar-large">
          <div class="mar-small">邮箱：</div>
          <div class="mar-small">
            <el-input
              v-model="email"
              placeholder="请输入生成口令发送的目标邮箱"
            ></el-input>
          </div>
        </div>

        <div class="mar-large">
          <div class="mar-small">
            生成结构化口令的概率阈值下限x：（以10^(-x)为单位）
          </div>
          <div class="mar-small">
            <el-input
              v-model="struct_prob"
              :placeholder="'输入范围' + this.PROB_MIN + '-' + this.PROB_MAX"
            ></el-input>
          </div>
        </div>

        <div class="mar-large">
          <div class="mar-small">
            生成最终口令的概率阈值下限x：（以10^(-x)为单位）
          </div>
          <div class="mar-small">
            <el-input
              v-model="final_prob"
              :placeholder="'输入范围' + this.PROB_MIN + '-' + this.PROB_MAX"
            ></el-input>
          </div>
        </div>

        <div class="mar-large">
          <div class="mar-small">生成口令的个数：</div>
          <div class="mar-small">
            <el-input
              v-model="num"
              :placeholder="
                '输入范围' + this.GEN_NUM_MIN + '-' + this.GEN_NUM_MAX
              "
            ></el-input>
          </div>
        </div>

        <div class="mar-large">
          <div class="mar-small">生成口令的长度下限：</div>
          <div class="mar-small">
            <el-input
              v-model="gen_len"
              :placeholder="
                '输入范围' + this.SEQ_MINLEN_MIN + '-' + this.SEQ_MINLEN_MAX
              "
            ></el-input>
          </div>
        </div>

        <div class="mar-large">
          <el-button class="mar-small" type="primary" @click="submit"
            >提交</el-button
          >
        </div>
      </div>
    </div>

    <el-dialog title="提示" :visible.sync="dialogVisible" width="30%">
      <span>训练结果稍后会发送至您的邮箱，请不要重复提交！</span>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="dialogVisible = false"
          >确 定</el-button
        >
      </span>
    </el-dialog>
  </div>
</template>

<script>
import axios from "axios";
import Qs from "qs";
import {
  EPOCH_MIN,
  EPOCH_MAX,
  PROB_MIN,
  PROB_MAX,
  GEN_NUM_MIN,
  GEN_NUM_MAX,
  SEQ_MINLEN_MIN,
  SEQ_MINLEN_MAX,
} from "../constant/parameters";
import { Message } from "element-ui";
export default {
  data() {
    return {
      EPOCH_MIN: EPOCH_MIN,
      EPOCH_MAX: EPOCH_MAX,
      PROB_MIN: PROB_MIN,
      PROB_MAX: PROB_MAX,
      GEN_NUM_MIN: GEN_NUM_MIN,
      GEN_NUM_MAX: GEN_NUM_MAX,
      SEQ_MINLEN_MIN: SEQ_MINLEN_MIN,
      SEQ_MINLEN_MAX: SEQ_MINLEN_MAX,
      type: "gen",
      email: null,
      extract_len: null,
      epoch: null,
      struct_prob: null,
      final_prob: null,
      num: null,
      gen_len: null,
      error: "",
      dialogVisible: false,
    };
  },
  methods: {
    toJson: function () {
      return (
        "module:pl,type:" +
        this.type +
        ",email:" +
        this.email +
        ",extract_len:" +
        (this.type == "train" ? this.extract_len : 0) +
        ",epoch:" +
        (this.type == "train" ? this.epoch : 0) +
        ",struct_prob:" +
        this.struct_prob +
        ",final_prob:" +
        this.final_prob +
        ",num:" +
        this.num +
        ",gen_len:" +
        this.gen_len
      );
    },
    check: function () {
      this.error = "";
      // emial
      const email_re =
        /^([a-zA-Z0-9]+[_|_|\-|.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|_|.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,6}$/;
      if (this.email === null || !email_re.test(this.email)) {
        this.error += "邮箱错误，";
      }
      const digits_re = /\d/;
      // extract_len
      if (
        this.type === "train" &&
        (!digits_re.test(this.extract_len) ||
          this.extract_len < this.SEQ_MINLEN_MIN ||
          this.extract_len > this.SEQ_MINLEN_MAX)
      ) {
        this.error += "提取口令长度下限错误，";
      }
      // epoch
      if (
        this.type === "train" &&
        (!digits_re.test(this.epoch) ||
          this.epoch < this.EPOCH_MIN ||
          this.epoch > this.EPOCH_MAX)
      ) {
        this.error += "训练轮数错误，";
      }
      // struct_prob
      if (
        !digits_re.test(this.struct_prob) ||
        this.struct_prob < this.PROB_MIN ||
        this.struct_prob > this.PROB_MAX
      ) {
        this.error += "结构化口令概率阈值下限错误，";
      }
      // struct_prob
      if (
        !digits_re.test(this.final_prob) ||
        this.final_prob < this.PROB_MIN ||
        this.final_prob > this.PROB_MAX
      ) {
        this.error += "最终口令概率阈值下限错误，";
      }
      // num
      if (
        !digits_re.test(this.num) ||
        this.num < this.GEN_NUM_MIN ||
        this.num > this.GEN_NUM_MAX
      ) {
        this.error += "口令数量错误，";
      }
      // gen_len
      if (
        !digits_re.test(this.gen_len) ||
        this.gen_len < this.SEQ_MINLEN_MIN ||
        this.gen_len > this.SEQ_MINLEN_MAX
      ) {
        this.error += "生成口令长度下限错误，";
      }

      if (this.error !== "") {
        Message.error(this.error);
        return false;
      } else {
        return true;
      }
    },
    submit: function () {
      if (this.check()) {
        this.dialogVisible = true;
        // console.log(this.toJson());
        let payload = {
          msg: this.toJson(),
        };
        axios({
          method: "get",
          params: payload,
          url: "http://localhost:8000/server/server",
        }).then((res) => {
          console.log("业务编号: " + res.data);
        });
      }
    },
  },
};
</script>


<style scoped>
.bac {
  background-color: var(--secondary-color-2);
}
.mar-small {
  margin: 8px;
}
.mar-large {
  margin: 15px;
  margin-right: 40px;
}
.half-width {
  width: 50%;
}
.pad {
  padding: 20px 20px 40px 20px;
}
</style>
