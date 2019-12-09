## Instructions
### Authors: Zetao Yu, Xichen Tan, Zimeng Zhuang, Yibing Lyu
### 0. Create a new EC2 instance (Ubuntu 18.04)

### 1. Clone this repo to AWS EC2 instance

```bash
git clone https://github.com/zetaoyu0029/low_rate_dos_tcp_attack
cd low_rate_dos_tcp_attack/
```

### 2. Setup the environment

```bash
chmod 777 setup.sh
sudo ./setup.sh
```

### 3. Run the experiment

```bash
sudo python run.py
```

### 4. Retrive the result (copy from EC2 to local)

Create a new terminal window and run:

```bash
scp -r -i KEY_PATH ubuntu@EC2_IP:~/low_rate_dos_tcp_attack/ LOCAL_DIR
```

The result `res_all.png` is located at `\Expr-xx-xx-xx--xx\rto...`.

## How to run with different parameters

Open `run.py` and modify the values in the loop condition.

`n_connections` is the number of tcp connections.

`minRTO` is minRTO.

`period` is the inter-attack period.
