<template>
  <div>
    <div class="mar-large full-width font-normal">
      这里是有关LSTM模型的介绍。
    </div>
    <div class="pad mar-large shadow border-radius font-normal bac">
      <el-tabs v-model="type">
        <el-tab-pane label="生成口令" name="gen">
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
                生成口令的概率阈值下限x：（以10^(-x)为单位）
              </div>
              <div class="mar-small">
                <el-input
                  v-model="prob"
                  :placeholder="
                    '输入范围' + this.PROB_MIN + '-' + this.PROB_MAX
                  "
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
              <div class="mar-small">生成口令的最小长度值：</div>
              <div class="mar-small">
                <el-input
                  v-model="len"
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
        </el-tab-pane>

        <el-tab-pane label="训练模型" name="train">
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
              <div class="mar-small">训练轮数：</div>
              <div class="mar-small">
                <el-input
                  v-model="epoch"
                  :placeholder="
                    '输入范围' + this.EPOCH_MIN + '-' + this.EPOCH_MAX
                  "
                ></el-input>
              </div>
            </div>

            <div class="mar-large">
              <div class="mar-small">
                生成口令的概率阈值下限x：（以10^(-x)为单位）
              </div>
              <div class="mar-small">
                <el-input
                  v-model="prob"
                  :placeholder="
                    '输入范围' + this.PROB_MIN + '-' + this.PROB_MAX
                  "
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
              <div class="mar-small">生成口令的最小长度值：</div>
              <div class="mar-small">
                <el-input
                  v-model="len"
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
        </el-tab-pane>
      </el-tabs>
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
      epoch: null,
      prob: null,
      num: null,
      len: null,
      error: "",
      dialogVisible: false,
    };
  },
  methods: {
    toJson: function () {
      return (
        "module:lstm,type:" +
        this.type +
        ",email:" +
        this.email +
        ",epoch:" +
        (this.type == "train" ? this.epoch : 0) +
        ",prob:" +
        this.prob +
        ",num:" +
        this.num +
        ",len:" +
        this.len
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
      // epoch
      const digits_re = /\d/;
      if (
        this.type === "train" &&
        (!digits_re.test(this.epoch) ||
          this.epoch < this.EPOCH_MIN ||
          this.epoch > this.EPOCH_MAX)
      ) {
        this.error += "训练轮数错误，";
      }
      // prob
      if (
        !digits_re.test(this.prob) ||
        this.prob < this.PROB_MIN ||
        this.prob > this.PROB_MAX
      ) {
        this.error += "概率阈值下限错误，";
      }
      // num
      if (
        !digits_re.test(this.num) ||
        this.num < this.GEN_NUM_MIN ||
        this.num > this.GEN_NUM_MAX
      ) {
        this.error += "口令数量错误，";
      }
      // len
      if (
        !digits_re.test(this.len) ||
        this.len < this.SEQ_MINLEN_MIN ||
        this.len > this.SEQ_MINLEN_MAX
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
        }
        axios({
          method: "get",
          params: payload,
          url: "http://localhost:8000/server/server"
        }).then(
          res => {
            console.log("业务编号: "+res.data)
          }
        )
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
  margin: 20px;
}
.half-width {
  width: 50%;
}
.pad {
  padding: 20px 20px 40px 20px;
}
</style>
